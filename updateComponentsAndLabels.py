from jira import JIRA
from credentials import username, password
debug = 0
jiraAttributes = 1

jira = JIRA(options={'server':'https://jira-stg.corp.linkedin.com:8443', 'verify':'/etc/ssl/certs/ca-bundle.crt'}, auth=(username, password) )


composedQuery = ""
project = "project=LLSTC"
summary = ""
if summary:
    summary = ' AND summary ~ "'+summary+'"'

assignee = ""
if assignee:
    assignee = ' AND asignee ~ "'+assignee+'"'

type = "task"
if type:
    type = ' AND type = "'+type+'"'

status = ""
if status:
    status = ' AND status = "'+status+'"'

composedQuery = project + summary + assignee + type + status

print(composedQuery)
issues_in_project = jira.search_issues(composedQuery, maxResults=1)

#issues_in_project = jira.search_issues('project=LLSTC AND summary ~ "Upgrade"', maxResults=2)

if jiraAttributes:
    for issue in issues_in_project:
        print("-------------- ", issue.key, "------------\n")
        print("Summary:", issue.fields.summary)
        print("Type:", issue.fields.issuetype)
        print("Status:", issue.fields.status)
        print("Assignee:", issue.fields.assignee)
        print("Reporter:", issue.fields.reporter)
        watcher = jira.watchers(issue)
        for watcher in watcher.watchers:
            print("Watchers:", watcher.emailAddress)
            print("")
        print("CreatedOn:", issue.fields.created)
        print("Updated:", issue.fields.updated)
        print("Components:", issue.fields.components)
        print("Labels:", issue.fields.labels)
        print("--------------------------\n")






#-------------Get list of all SSO and LMS components in project-------------
jiraProject = jira.project('LLSTC')
components = jira.project_components(jiraProject)
componentList = []
if debug:
    print("-------------beginning of LMS Components------------\n")
for c in components:
    if "LMS" in c.name:
        componentList.append(c.name)
        if debug:
            print(c.name)
            print("-------------end of LMS Components------------\n")
            print("-------------beginning of Auth Components------------\n")
for c in components:
    if "SSO" in c.name:
        componentList.append(c.name)
        if debug:
            print(c.name)
            print("-------------end of Auth Components------------\n")
            print(componentList)


#---------------Parse description for LMS and Auth Type--------------------
for issue in issues_in_project:
    print('{}: {}, {}'.format(issue.key, issue.fields.summary, issue.fields.components))
    existingComponents = []
    description = issue.fields.description
    if not description:
        break
    lms = ""
    for lmsType in description.split("\n"):
        if "LMS" in lmsType:
            lms = lmsType.strip()
            lms = lms.replace("LMS: ",'')
            lms = lms.replace('"','')
            lms = lms.replace('[','')
            lms = lms.replace(']','')
    print("LMS = " + lms)
    auth = ""
    for item in description.split("\n"):
        if "Auth" in item:
            auth = item.strip()
            auth = auth.replace("Auth Method:",'')
            auth = auth.replace('"','')
            auth = auth.replace('[','')
            auth = auth.replace(']','')
    auth = auth.strip()
    if not auth:
        auth = "Standard Auth"
    if not lms:
        lms = "No learning management system"

    if debug:
        print("SSO = " + auth)
        print("splitting successful", auth, lms)

    for component in issue.fields.components:
        existingComponents.append({"name": component.name})
    if debug:
        print(existingComponents)
        print("component list ------", componentList)
    iteration = 0
    for c in componentList:

        if debug:
            print("---------------------------")
            print("Iteration:", iteration)
            print("SSO inside of for loop:", auth)
            print("LMS inside of for loop:", lms)
            print("component inside of for loop:", c)
            print("---------------------------")
            iteration = iteration + 1

        if (lms in c) or (auth in c):
            print("Found A LMS Match! With: ", c)
            existingComponents.append({"name": c})
            print("---------------------------")


    if debug:
        print(existingComponents)
    issue.update(fields={"components": existingComponents})
    print("components updated", issue.key, "New component list:\n", existingComponents)
