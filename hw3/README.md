# 3. Rule-based Natural Language Understanding

This document describes the intents which are parsed in Task Management domain.

The solution for this task is in following files:

- `/dialmonkey/nlu/task_management/parser.py`
- `/dialmonkey/nlu/task_management/string_func.py`
- `/dialmonkey/nlu/task_management/preprocessing.py`
- `/conf/task_management.yaml`
- `/hw5/examples.tsv`

### greet()

- The systems replies with greet() intent, if the system receive greetings like: hello, good day, ...

### get_tasks

- The user is going to ask the system if there are some scheduled tasks for a given time.
  - day = today, tomorrow, yesterday, any_day,
  - time = morning, evening, afternoon, 10 am, 22 pm

### create_task

- The user is going to create an event by telling the system what kind of event does he want to create. Our parser
  - event = meeting, lecture, gym
  - day = today, tomorrow, yesterday, any_day,
  - time = morning, evening, afternoon, 10 am, 22 pm

### update_task

- Edits information about the plan.
  - keywords = keywords in the name of the event
  - day = today, tomorrow, yesterday, any_day,
  - time = morning, evening, afternoon, 10 am, 22 pm

### delete_task

- keywords = keywords in the name of the even

```html
Create
<name>
  and schedule it on
  <time>
    create_task(name=<name
      >, time=<time
        >) Create the event
        <name>
          and schedule it on
          <time>
            create_task(name=<name
              >, time=<time
                >) Create the task
                <name>
                  and schedule it on
                  <time>
                    create_task(name=<name
                      >, time=<time
                        >) Create the plan
                        <name>
                          and schedule it on
                          <time>
                            create_task(name=<name
                              >, time=<time
                                >) Delete
                                <name>
                                  delete_task(name=<name
                                    >) Delete the event
                                    <name>
                                      delete_task(name=<name
                                        >) Delete the task
                                        <name>
                                          delete_task(name=<name
                                            >) Delete the plan
                                            <name>
                                              delete_task(name=<name
                                                >) Get all events for
                                                <time>
                                                  get_tasks(time=<time
                                                    >) Get all tasks for
                                                    <time>
                                                      get_tasks(time=<time
                                                        >) Get all plans for
                                                        <time>
                                                          get_tasks(time=<time
                                                            >) Give me more
                                                            information about
                                                            <name>
                                                              get_task(name=<name
                                                                >) Tell me some
                                                                details about
                                                                <name>
                                                                  get_task(name=<name
                                                                    >) Get
                                                                    information
                                                                    about
                                                                    <name>
                                                                      get_task(name=<name
                                                                        >) Get
                                                                        all
                                                                        meetings
                                                                        for
                                                                        <time>
                                                                          get_tasks(time=<time
                                                                            >)</time
                                                                          ></time
                                                                        ></name
                                                                      ></name
                                                                    ></name
                                                                  ></name
                                                                ></name
                                                              ></name
                                                            ></time
                                                          ></time
                                                        ></time
                                                      ></time
                                                    ></time
                                                  ></time
                                                ></name
                                              ></name
                                            ></name
                                          ></name
                                        ></name
                                      ></name
                                    ></name
                                  ></name
                                ></time
                              ></name
                            ></time
                          ></name
                        ></time
                      ></name
                    ></time
                  ></name
                ></time
              ></name
            ></time
          ></name
        ></time
      ></name
    ></time
  ></name
>
```
