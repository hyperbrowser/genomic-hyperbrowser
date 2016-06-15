# Galaxy ProTo
## Introduction
The Galaxy Prototyping Tool API (Galaxy ProTo) is an extension of the Galaxy web-based platform for data intensive biomedical research, which is available from [galaxyproject.org](https://galaxyproject.org). Galaxy ProTo is a new tool building methodology introduced by the [Genomic HyperBrowser project] (https://hyperbrowser.uio.no) as an unofficial alternative for defining Galaxy tools. Galaxy ProTo provides:

- Rapid and simple development of Galaxy tools using Python code only (no XML knowledge needed)
- Fully on-the-fly development, no need to restart the server or reload the tool to witness changes
- Fully dynamic user interface, able to change the interface based upon e.g. earlier selection, input files or database queries

## Background

In addition to being a feature-rich framework for biomedical research, Galaxy can also be thought of as a simple way to provide web access to locally developed functionality. Galaxy can for instance be used by master students to showcase their developed functionality to the supervisors and examiners, or it can be used by researchers to easily provide access to their *ad hoc* developed scripts. For such use, however, Galaxy poses some limitations. For one, the developer needs to learn the XML format used by Galaxy, with all the twists and turns inherent in the format. Also, the format itself has limited support for dynamics in the parameter option boxes, e.g. for providing the user with direct feedback based upon dynamic calculations within the interface itself.

## Features

Instead of XML files, Galaxy ProTo supports defining the user interface of a tool as a Python class. There are no limitations to what kind of code that can be executed to generate the interface. For instance one could read the beginning of an input file and provide dynamic options based on the file contents. When developing a ProTo tool, results of changes in the code can be witnessed on-the-fly in a web browser; there is no need to reload the tool or restart the Galaxy server. When development is finished, a ProTo tool can be easily be installed into the Galaxy tool menu alongside the standard Galaxy tools. Galaxy ProTo thus empowers developers without Galaxy experience to easily develop Galaxy tools, both for prototyping purposes, but also for developing fully functional, interactive tools.

## Known limitations

- Galaxy ProTo tools will not run as part of a Galaxy workflow. Support for this might de developed if the need is high, but it is not a priority right now, as Galaxy ProTo is envisioned first and foremost as a way to provide easy and dynamic interaction directly with the user.
- Galaxy ProTo works best connected to a PostgreSQL database (as recommended for [production Galaxy instances] (https://wiki.galaxyproject.org/Admin/Config/Performance/ProductionServer)). It will work out-of-the-box with the default SQLite database, but due to a basically unfixable deadlock issue, the user will experience significant waiting time when using the tools. Using SQLite, the opening of tools will once in a while fail and time out after 15 seconds, after which the tool reloads for another try. Because of this is it highly recommended to use PostgreSQL instead of SQLite.
- Galaxy ProTo has only been tested on Linux-based operating systems. It will probably also work on Mac OS X, and probably not on Windows.
- The "Run this job again" functionality of Galaxy will break for old history elements if the "proto_id_secret" configuration options is changed in the "galaxy.ini" file.
- ProTo tools are not supported in Galaxy Tool Shed, mainly because the API is an unofficial alternative to the Galaxy XML.
- Tested mainly with Chrome and Firefox web browsers.

## Installation

It is highly recommended that users of Galaxy ProTo create a GitHub fork of the project to host their developed ProTo tools, so this guide will follow that approach. If, for some reason, you would like to work locally on the server only, please just skip item 1 and 2 and use the URL "https://github.com/elixir-no-nels/proto" in item 3.i.

1. Create a github user (if you do not already have one), at https://github.com, and sign in.
2. Fork Galaxy Proto:
  1. Access "https://github.com/elixir-no-nels/proto"
  2. Click the fork button and follow the guide
  3. Note the URL to your forked repo, e.g. "https://github.com/user/proto"
3. Clone your GitHub fork to your computer/server:
  1. `git clone https://github.com/user/proto galaxy_proto` using the URL to your forked repo
  2. `cd "galaxy_proto"`
  3. `git remote add upstream https://github.com/elixir-no-nels/proto`
  4. `git checkout proto_master`
4. Create your own GIT branch for your tools, in this guide named "myproject_dev":
  1. `git branch "myproject_dev"`
  2. `git checkout "myproject_dev"`
5. Set up the main Galaxy config files:
  1. `cd config`
  2. `cp galaxy.ini.sample galaxy.ini`
  3. `cp tool_conf.xml.sample tool_conf.xml`
6. Set up an empty PostgreSQL database (follow a PostgreSQL tutorial to do this). See "Known Limitations" above.
7. Edit galaxy.ini:
  1. Uncomment "port" and set it to an unused port number (or keep the default 8080 if you want).
  2. Uncomment "host" and set it to `0.0.0.0` (given that you want to access the Galaxy ProTo web server from other computers).
  3. Uncomment "database_connection" and set it to point to your PostgreSQL database, as explained in the [Galaxy Wiki] (https://wiki.galaxyproject.org/Admin/Config/Performance/ProductionServer#Switching_to_a_database_server). 
  4. Uncomment "admin_users" and add the email address(es) for the admins. An adimn account is needed to publish finished ProTo tools to the tool menu. You will need to register with the same address in Galaxy to get the admin account.
  5. Uncomment "id_secret" and set it to the result of the one-liner generation code in the comments.
  6. Uncomment "restricted_users" and add any users that need access to private development tools (e.g. developers or test users). Admn users are by default also restricted users and no not need to be listed twice.
  7. Uncomment "proto_id_secret" and set it to the result of the one-liner generation code in the comments, but with a different code than "id_secret". NOTE: This step is important if you want to maintain the redo functionality, see "Known Limitations" above.
8. Start up Galaxy ProTo:
  1. `cd ..` (to exit the "config" directory).
  2. `./run.sh`. The Galaxy should now be accessible from e.g. http://yourserver.edu:8080, where the hostname and port will change according to your setup.
  - For making Galaxy run in the background, use `./run.sh --daemon` to start it and `./run.sh --stop-daemon` to stop it.
9. In order to commit code changes and push to your github fork, run:
    - `git add $FILE` for all new and changed files
    - `git commit -m "Some nice commit message"`
    - `git push origin myproject_dev` to push all local commits to GitHub

## Tool development

Tool development in ProTo consists of three major steps, each handled by dedicated tool under the tool header "ProTo development tools":

1. **ProTo tool generator**: This tool is used to dynamically generate a Python module (i.e. a *.py file) that defines a new ProTo tool. The module is a duplicate of a selected tool template, containing a very simple usage example.
2. **ProTo tool explorer**: After a Python module has been generated, one needs to edit the *.py file in some editor (preferably an IDE, like PyCharm). One can then witness the creation of the tool on-the-fly using the ProTo tool explorer. Just save the file, and the user interface of the tool will be updated. The ProTo tool explorer contains all the tools that has not been installed (i.e. is under development).
3. **ProTo tool installer**: After the tool has been finalized, it can be published as a separate tool in the tool menu. A restricted user can carry out this with the ProTo tool installer, but an administrator needs to refresh the tool menu for the new tool to appear.

### Documentation of the API

The complete API is documented as pydoc strings within the [ToolTemplate.py] (lib/proto/tools/ToolTemplate.py) file, and a HTML compilation of the documentation (with some manual modifications) is available in the [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) file.

A basic tutorial has yet to be written, but here are some points to get you started:

1. A ProTo tool is a subclass of the GeneralGuiTool class. The user interface and functionality of the tool is defined based upon whether certain methods are available in the subclass (uncommented from the [ToolTemplate.py] (lib/proto/tools/ToolTemplate.py) or [ToolTemplateMinimal.py] (lib/proto/tools/ToolTemplateMinimal.py) file), and if available, the exact content which is returned from the method. 
2. The minimal set of methods to be defined is `getToolName()`, `getInputBoxNames()` and `execute()`. which will produce a tool existing of a single execute button.
3. Adding other input (and output) boxes is a matter of first defining them in the return statement of getInputBoxNames() with a certain key, e.g. "histSelect". Secondly, one needs to implement a method `getOptionsBoxKey`, exchanging the actual key string in the method, in this example `getOptionsBoxHistSelect`. The return value of this method defines the type of input field, e.g. returning a string creates a text box, while a list of strings creates a selection list. See the [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) documentation for the complete list of inpute fields.
4. The parameter `prevChoices` provided to the `getOptionsBox...()` methods is a namedtuple object of all previous options boxes (including the previous content of the current options box). One can access previous selection by using standard member access, e.g. `prevChoices.histSelect`. Similarly the parameter `choices` provided to the `execute()` method and others contain the full list of option box selections, in the same format.
5. The parameter `galaxyFn` contains the disk path to the output dataset of the tool. Please write tool output to this file path. See [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) for more details.
