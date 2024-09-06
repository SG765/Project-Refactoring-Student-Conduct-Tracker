Student Conduct Tracker Project

Group: CTRL-ALT-DELETE

Postman Documentation: [https://documenter.getpostman.com/view/30409872/2s9YJjSzQF ](https://documenter.getpostman.com/view/30262830/2s9YeK5Ai4)

# Testing with the Development Environment (Codespaces, Gitpod, etc)
*Requires a Postman Account
1. Install dependiences ```pip install -r requirements.txt ```
2. Initalize db ```flask init```
3. Run the server ```flask run``` and change server visibility to public
5. Use the Postman link above to run the collection in Postman
6. Create a postman environment with the following variables; the base_url is the url of the development server, the tokens can be gotten from running the login requests
 ![image](https://github.com/user-attachments/assets/ece17207-7834-4a60-bc75-9f00bb0eb05d)
7. The Postman Documentation contains details and examples on how to run the various requests, test files 'students.csv' & 'updatedTest.csv' can be accessed via the github repo for use in testing the upload requests. 


---
# Dependencies
* Python3/pip3
* Packages listed in requirements.txt

# Installing Dependencies
```bash
$ pip install -r requirements.txt
```
