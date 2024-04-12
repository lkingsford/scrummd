## ScrumMD

![Logo](docs/images/logo.png)

**ScrumMD** started with a question: What if we could have a scrum board driven entirely by md files and the CLI, and use it with git?

I know that it's going to be of niche use, but it opens up a number of great ways to do the scrum process. For instance:

-   You can run standup for `sprint1` with:

```bash
vim `sbl -b sprint1`
```

-   You can manage your cards with git...
-   ... and can add them in the repository that they are for
-   It's all text - so integrate with whatever you want

The very basics are that you have a `scrum` folder, and you can put cards inside
it. A card is very simple - it's just a markdown file with at least a summary
field. For instance -

```markdown
---
Summary: Make the thing
---

# Description

Take the steps to make the thing

# Dependencies

-   [[thing02]]
-   [[thing03]]
```

would be a completely valid card that can be explored with ScrumMD. But - per
the documentation - it does a bunch more!

There's also some funky other tools like `sboard` that let you view a visual
representation of the Scrum board in the console - for instance:

```text
$ sboard --group-by status
|not fully defined  |ready              |in progress        |in testing         |done               |None               |
|-------------------|-------------------|-------------------|-------------------|-------------------|-------------------|
|cli008             |cli028             |cli034             |                   |cli018             |v0-1               |
|Permit newlines in…|Allow underline he…|Show scrum board o…|                   |`sbl` Group By     |Items remaining to…|
|                   |                   |                   |                   |                   |                   |
|cli029             |cli032             |                   |                   |cli019             |                   |
|Allow subheadings …|Write access to pr…|                   |                   |String property af…|                   |
|                   |                   |                   |                   |                   |                   |
```

## Documentation

Find it all over on [Read The Docs](https://scrummd.readthedocs.io/). There's a fair bit of detail, and a tutorial for getting started.

## License

This is published under the [GNU General Public License v3.0](LICENSE.md). I am willing to discuss making it available under another license, or providing pai
