# API/Backend Calls

In this assignment, we have implemented API calls. We chose the open API of the task management application, Todoist.
You can find the documentation of the API on this website: https://developer.todoist.com/guides/#developing-with-todoist

To use the API calls you have to do the following steps:

1. You have to install `todoist-python` package which is also mentioned in `requirements.txt`

```
pip install todoist-python
```

2. You have to pass the authentication token in the constructor of the TaskManagementRepository class which is located in
   `dialmonkey/repositories/task_management.py`. For this assignment, we have pushed the authentication token in the git repository.
   It is hardcoded in the TaskManagementRepository class.
   You can look at tasks on the account with these credentials:

   email: todoist.chatbot@gmail.com

   password: heslo123
