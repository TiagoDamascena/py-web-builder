This project arose from the need to build static websites easily
maintainable, allowing html templates to be combined with markdown
content.

## Instalation
For now you need to clone or download this repository and run the builder.py file from your project root folder.

### Dependencies
#### Python Markdown 2
Used to convert convert markdown files to HTML, you can read more about instalation [here](https://github.com/trentm/python-markdown2)

## How to use
First create a file called ```web-builder.json``` on your project root folder, this file will contain all your build configuration, it will look something like this:

```json
{
  "config": {
    "build_folder": "dist/"
  },
  "copy": [
    "css/",
    "img/",
    "js/",
    ".htaccess"
  ],
  "build": [
    "index.html",
    "content/"
  ]
}
```
#### Config
This section contain general configurations, for now accept only the destination folder of the build.

#### Copy
Is an array with all the files that will be copied to the destination folder, accepts files and entire folders.

#### Build
Is an array with all files that will be builded, accepts files and folders in markdown or html
