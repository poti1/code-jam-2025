<div align="center">
    <picture>
      <img width="150px" alt="pybrowser logo" src="./docs/assets/pybrowser_logo.png">
    </picture>
      <div align="center">
         <h1>pyBrowser</h1>
      </div>
</div>

## Table of Contents

* [Introduction](#introduction)
  * [Features](#features)
  * [Code Jam 12 Theme Connection](#code-jam-12-theme-connection)
* [pyBrowser in Action](#pybrowser-in-action)
* [Libraries used](#libraries-used)
* [Contributors](#contributors)
* [Attribution](#attribution)

## Introduction

PyBrowser is a simple web browser built using the pyodide and pyscript packages.

### Features

*   Search with Mojeek right from the address bar
*   Go back and forth to visited pages
*   Page reload
*   Sleek and Modern UI
*   Pages are displayed in white font HTML
*   Mostly working HTML parser
*   In-browser page requests
*   Cookies!

### Code Jam 12 Theme Connection

Browser'ception! Aside from using Python running in the browser for a complex tool, pyBrowser is definitely the wrong tool for the job of browsing the web because it's a browser running inside another, likely better functioning, browser.

## pyBrowser in Action

Navigating to [example.com](https://www.example.com):

![Navigating to https://www.example.com from the pyBrowser address bar.](/docs/assets/pyBrowserEx.gif)

Searching "cats" in the address bar:

![Searching for "cats" in the address bar using the Mojeek search engine.](/docs/assets/pyBrowserSearchEx.gif)

Forward, Backward, and Reload functionalities:

![Navigating to example.com, then example.org going back, forward, then reloading the page](/docs/assets/pyBrowserForwardBackwardReload.gif)

## Libraries Used

We mainly used pyodide to do a lot on the backend in-browser making requests and listening to button-click and keyboard-press events. Pyscript was used to manipulate the browser HTML and utilize the Javascript API from Python. Other functionalities such as cookies, HTML tokenization/HTML parsing, and rendering were all hand-rolled.

## Contributors

* <a href="https://github.com/xing216">Xing</a> implemented/integrated the HTML parser, helped with documentation, and coded the Canvas rendering API
* <a href="https://github.com/Gimpy3887">Gimpy</a> implemented the frontend, backend api, wrote the documentation, and managed the repo
* <a href="https://github.com/bast0006">Cat(cat.cat())</a> created/integrated the cookies feature
* <a href="https://github.com/cameronabel">Cameron</a> created the CSS parser
* <a href="https://github.com/poti1">timka7060</a> (Team Lead) had minor contributions to a different version of the CSS parser and minor repo management

## Attribution
Free resources used to make the pyBrowser logo and its user interface.  

<a href="https://www.flaticon.com/free-icons/pacific" title="pacific icons">Pacific icons created by Kalashnyk - Flaticon</a>  
<a href="https://www.flaticon.com/free-icons/snake" title="snake icons">Snake icons created by Vitaly Gorbachev - Flaticon</a>  
<a href="https://www.figma.com/community/file/1159604531253325245" title="ui icons">Icon pack | 1600+ icons | 160 free icons created by HI.icons - Figma</a>
