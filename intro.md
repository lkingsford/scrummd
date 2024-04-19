All I wanted was a Scrum tool that I would enjoy using. I was grumpy at
something to do with Jira, and I started thinking about how a Scrum team would
manage itself without it. I mean - originally, most Scrum teams just used a
whiteboard.

I had a thought. One of those niggling thoughts you can't quite shake, so you've
got to do something about it, even though you know it's a terrible idea that
you're pretty certain only you'd like.

What if I could just shove all of my cards into markdown files? And what if I
could then do the 'Scrum things' with my text editor and the command line?

So - I did what anybody struck by a niggling thought like that would do. I
wanted to see what such a tool might look like, so I started writing ScrumMD.

Hi - I'm Lachlan Kingsford, the author of ScrumMD. I'm a scrum.org certified
scrum-master, but I spend most of my day creating software.

The Scrum guide says that a Scrum team is supposed to be 'self-managing'. Since
I spend so much time writing code, there are some ramifications:

-   I love text files. Love, love, love text files. You can do anything with text
    files - you can store them how you want, modify them to your hearts content,
    version track them, throw them in Pandoc to turn to pretty much any format.
    Heck - my wife has been witness to me using Visual Studio Code with Vim
    keybindings to write song lyrics.

-   I love the terminal. Sure - you can give me an API and I can write some code
    to connect to it, but lets face it, almost every tool aimed at non-programmers
    really wants you to use the GUI.

-   I like my data being local. This one might sound a bit weird to some of you -
    but I've been spoiled by Git. I like having my local copy of data to work on,
    and then explicitly sharing it around.

I suspect I'm not alone in those three points. I The more I worked on ScrumMD,
and the more I thought about it, the more I realised that this was actually
something kinda funky - but admittedly niche - that I wanted. After all - a
self-organising team of people like me really might like to manage their Scrum
boards using the tooling they're most comfortable with.

So - we get ScrumMD: A tool for self organising teams.

ScrumMD is already freely available. If you've got Python 3.10 or higher - you
can go pip install it right now. It's GPL licensed, so - if the text files
aren't enough - you can hack away at your hearts content. Documentation is
already available on readthedocs.io - and should be linked to this video.

What are the ramifications of my decisions?

-   Text means that you can do things like include your cards or tickets with the
    repos they effect. There's nothing even stopping your team managing them with
    git, and using submodules to have them in multiple repos at once.

-   You can chain things together. You can run stand-up by getting a list of cards
    in the current sprint, group them by status, just show the paths to the cards
    and load them all in vim to go through. Then, split the screen, and call
    `sboard` to show the board with `watch` to update as you're going.

-   You can highly customize your configuration to your teams needs with a text
    configuration files, that you can version track too. For instance, needing
    status to always be on every story card, and always be 'Ready for
    Development', 'In Progress' or 'Done'. The customizability means that there's
    nothing stopping you using it anywhere where tracking a collection of cards
    might be helpful - for instance, issues, support tickets, a kanban board,
    test cases, documented decisions.

-   A developer theoretically never needs to leave their console or text editor
    to be part of the Scrum process. This means that they can better maintain
    a flow state when (for instance) checking or updating the requirements for
    a card they are implementing

-   You will make people uncomfortable, and challenge them based on the idea of
    'a self-managing team'. I am confident that the tools are simple enough to
    use that a scrum-master (or scrum lead) or product owner with some technical
    experience will be able to work with ScrumMD - but it is very specifically
    optimised for the team to be able to work closely together. An organisation
    that applies metrics between teams, or performs Scrum At Scale might
    struggle to adapt to a tool that is so 'use this as you see fit'. But -
    there is nothing in the tool that prevents it, and a responsive organisation
    might be able to adapt to it - particularly given how friendly the formats
    are to being parsed and distributed by other tools.

So - if you're in a technical agile team, or responsible for a technical agile
team, you might want to give it a shot. I'm proud of this tool I've made - and
I already enjoy using it. You might too.

I'm going to quickly show you some of the ways you can use it.

So - you can see here, I've got a folder of the cards to track the development
of ScrumMD itself.

Let's firstly have a look at one of the cards. As you can see - it's a fairly
plain markdown file. We do have a requirement that there is always a 'summary'
field, but beyond that, it's up to you to set the required fields and
potentially permitted values for ScrumMD to enforce.

We can look at this in `scard`. The big thing that will do is dereference those
references to cards, so you can quickly see more information about them. I've
configured it to show the status of the cards - but in a team, you might
configure it to show the status and assignee. It's particularly helpful for
creating reports - for instance, here I've collected all the cards I planned
to release in v0.1.

But - the big helpful tool in `sbl` - short for Scrum Back Log.

If I use `sbl`, I can show you a list of all of the cards. I can group them,
filter them and sort them too. It shows you a collection of cards - so, I could
show all the stories or bugs. If I created a backlog collection - I could show
that. Or - if I've referred to other cards (like I how I have my list of
dependencies for cli017 here), I can list those too.

There are some options for output. So - if I go `--bare` - you'll see just the
paths of the fields. This means you can pipe it into another tool - so, you
can see here, I've loaded all of the cards, in status order, directly into vim -
like I might do during a stand-up.

We've also got a specific output just to help you get a visual representation of
what's there - so we can use `sboard` with a group - for instance here, by
status.

There are a few more things you can do with it that I haven't shown. There's
some more options to configure. There's `svalid`, designed to go into a CI/CD
pipeline that will return a non-zero exit code if there's any issues with your
card repository (such as a card missing a required field). There's some tagging
options to help you collect cards - but, it's an intentionally minimal suite.
