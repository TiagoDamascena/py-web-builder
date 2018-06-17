This project arose from the need to build static websites easily
maintainable, allowing html templates to be combined with markdown
content.

## Instalation
For now you need to clone or download this repository and install the dependencies.

### Dependencies
#### Python Markdown 2
Used to convert convert markdown files to HTML, you can read more about instalation [here](https://github.com/trentm/python-markdown2)

## How to use
### Configuration
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
Is an array with all files that will be builded, accepts files and folders in markdown or html.

### Creating Templates
A template file is simply a conventional html file with comments like this:
```html
<!-- pwb:content('title') -->
```
This comment represents a point in the file to be replaced by content of another file.

### Using a Template
To use a template you need to declare that your file extends a template by adding this comment with the path of the file to be extended (the path need to be relative of the root of the project):  
```html
<!-- pwb:extends('template/base.html') -->
```  
And to place your content inside de template you need to put it inside section start and end tags like this:
```html
<!-- pwb:section('text') -->
  <p>Your content goes here</p>
<!-- pwb:end-section -->
```
Each file can only extends one file, but can have how many content and sections you want.

Markdown files are automatically converted to html if the extension is properly set to .md

All generated files will be .html, no matter the extensio it had before.
