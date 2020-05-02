from pathlib import Path
from bs4 import BeautifulSoup
import requests
import time
import os
from multiprocessing import Pool
import re
import webbrowser


class MoodleScraper:

    BASE_URL = "https://moodle.covenantuniversity.edu.ng/login/index.php"
    COURSES_PAGE_URL = "https://moodle.covenantuniversity.edu.ng/?redirect=0" 

    def __init__(self, username, passsword):
        """Get the username, password to instantiate as login data"""
        self._login_data = {
            "anchor": "",
            "rememberusername" : "1"
        }
        self._login_data["username"] = username
        self._login_data["password"] = passsword
        self._headers = {
            "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
            "Referer": "https://moodle.covenantuniversity.edu.ng/login/index.php",
            "Cookie": "MoodleSession=v468a9r9gdta0vjlqm86maq42s",
            "Connection": "keep-alive",
        }
        self._session = requests.Session()
        try:
            request = self._session.get(MoodleScraper.BASE_URL, headers=self._headers)
            first_soup = BeautifulSoup(request.content, "html5lib")
            self._login_data["logintoken"] = first_soup.find("input", {"name":"logintoken"})["value"]
            self._headers = request.request.headers # Get header for cookie management
        except Exception as e:
            raise Exception(e)

    def login_student(self):
        """Post login data and check for login errors"""
        try:
            request = self._session.post(MoodleScraper.BASE_URL, data=self._login_data, headers=self._headers)
            login_soup = BeautifulSoup(request.content, "html5lib")
            error = login_soup.find("div", {"role":"alert"}).get_text().lower() # get alert error from the page
            if "invalid" in error:
                return error.upper()
            print("You are logged in")
            self._headers = request.request.headers # Get cookies as it changes upon login
            return self._headers
        except Exception as e:
            raise Exception(e)

    def get_course_links(self):
        username = self._login_data["username"]
        try:
            request = self._session.get(MoodleScraper.COURSES_PAGE_URL, headers=self._headers)
            courses_soup = BeautifulSoup(request.content, "html5lib")
            h_fours =[]
            card_decks = courses_soup.find_all("div", class_="card-deck")
            for card_deck in card_decks:
                h_fours += card_deck.find_all("h4", class_="card-title")
            detail =[]
            with open(f"{username}-course.txt", "w") as user_courses:
                for h_four in h_fours:
                    course_link = h_four.find("a")["href"]
                    course_name = h_four.find("a").string
                    detail += [course_link, course_name]
                    user_courses.write(course_link + "\n" + course_name + "\n")
                print("done")
            return detail
        
        except Exception as e:
            raise Exception(e)
            
    def get_course_pages(self, check=False, course=None):
        """Get a particular course page or every course in the txt file"""
        request = None
        username = self._login_data["username"]
        file_location = Path(f"{username}-course.txt").exists() 
        if not file_location:
            self.get_course_links() # run get_course_links if path doesn't exist

        with open(f"{username}-course.txt", "r") as user_courses:
            data = user_courses.read().splitlines(False)
            gone_to_list = []
            for index in range(0, len(data), 2):
                if not course:
                    word = f"Went to {data[index+1]} section"
                    gone_to_list.append(word)
                    request = self._session.get(data[index], headers=self._headers)
                    if check and request: # Check for request from either full courses or just particular ones
                        self.check_for_quizzes(username, request)
                    print(word)
                    time.sleep(1)
                    
            
                if (course):
                    if (course.upper() in data[index+1]):
                        print(f"Going to {data[index+1]} section")
                        request = self._session.get(data[index], headers=self._headers)
                        if check and request: # Check for request from either full courses or just particular ones
                            self.check_for_quizzes(username, request)
                        break
            return gone_to_list
                
    def check_for_quizzes(self, username, request):
        """Gets called from get_courses and checks if new assignment is uploaded"""
        quizzes_list = [] 
        assignment_list = []
        quiz_soup = BeautifulSoup(request.content, "html5lib")
        span_items = quiz_soup.find_all("span", class_="instancename")
        for item in span_items:
            item = item.get_text().lower()
            if "quiz" in item:
                print("\t-Quiz")
                quizzes_list.append(item) 
            if "assignment" in item:
                print("\t-Assignment")
                assignment_list.append(item)
        # CHECK IF THE FILES QUIZZES IS UPDATED
        # with open(f"{username}-assignments.txt", "r") as user_assignment: 
        #     data_from_files = user_assignment.read().splitlines(False)
        #     if (data_from_files == assignment_list):
        #         pass
        #     else:
        #         fileee=open("assignments.txt", "w")
        #         for lines in assignment_list:
        #             fileee.write(lines+"\n")
        #     fileee.close()
        
   
    def get_download_links(self, course):
        username = self._login_data["username"]
        with open(f"{username}-course.txt", "r") as user_courses:
            data = user_courses.read().splitlines(False)
            for index in range(1, len(data), 2):
                if course in data[index]:
                    course_link = data[index-1]
                    
                    break
        
        request = self._session.get(course_link, headers=self._headers, allow_redirects=True)
        dwnld_soup = BeautifulSoup(request.content, "html5lib")
        sections = dwnld_soup.find_all("li", {"class":"section"})

        with open(f"{username}-{course}.txt", "w") as course_link:
            for section in sections:
                head_with_links = section.find_all("div", {"class":"activityinstance"})
                for head in head_with_links:
                    link = head.find("a")["href"]
                    name = head.find("span", class_="instancename").next_element
                    
                    course_link.write(link + "\n" + name + "\n") 
 

    def download_course_file(self, course):
        username = self._login_data["username"]
        p = Path(f"{username}-{course}.txt").exists()
        if not p:
            self.get_download_links(course)
        statime = time.time()
        if __name__ == "__main__":
            with Pool() as p:  
                with open(f"{username}-{course}.txt", "r") as course_link:
                    data = course_link.read().splitlines(False)[::2]
                    p.map(self.download, data)
        print(f"Process done {time.time()-statime}")

    def _is_downloadable(self, url):
        """Does the url contain a downloadable resource"""
        response = self._session.get(url, allow_redirects=True, headers=self._headers)
        header = response.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False
        return response

    def download(self, url):
        response = self._is_downloadable(url)
        if response:
            name = response.headers.get('content-disposition')
            fname = re.findall('filename=(.+)', name)
            if len(fname) != 0:
                filename = fname[0]
                print(filename)
            else :
                filename = "Lecture note"
            with open(filename, 'wb') as files:
                files.write(response.content)


    def end_process(self):
        self._session = self._session.close()
        print("bye bye")
