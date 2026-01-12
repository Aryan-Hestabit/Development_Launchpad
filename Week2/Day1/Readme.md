# Day 1 — Semantic HTML5 Blog Page

## Overview
This project is part of Day 1 of the training program and focuses on building a fully semantic HTML5 blog page without using CSS or non-semantic containers. The goal is to understand page structure, accessibility, and correct usage of HTML5 semantic elements.

## Objectives
1. Understand HTML document structure and metadata
2. Use semantic HTML5 elements correctly
3. Build a structured blog layout without <div>
4. Implement accessible navigation, forms, and media
5. Practice internal linking within a webpage

## Project Structure
```bash
.
├── blog.html
├── images/
│   ├── image1.jpg
│   ├── image2.jpg
│   ├── image3.jpg
│   ├── image5.jpg
│   └── video.mp4
```

## Page Structure Breakdown
1. Header & Navigation
Uses <header> and <nav>

Navigation links are internally mapped to page sections using IDs

Improves usability and accessibility with aria-label

2. Main Content

The ```<main>``` section is divided into two primary sections:

<b>Featured Posts </b>

Implemented using ```<section>``` and ```<article>```
Each post contains:
   ```<figure>``` and ```<img>```
   ```<header>``` with title and publication date
Images are uniformly sized using HTML attributes

<b>Blog Posts </b>

Individual blog articles created using ```<article>```
Includes:
  Text-based blogs
  A blog post with embedded ```<video>```
  Proper metadata using ```<time>```

## Media Usage

Images stored in a dedicated images/ folder <br>
Uniform sizing using width and height attributes <br>
Video embedded using the ```<video>``` element with controls enabled

## Sidebar Functionality

The ```<aside>``` section contains:
   Search form with label and validation
   Recent posts list
   Categories list
   Newsletter subscription form with email validation

## Forms & Validation

Forms use semantic ```<form>```, ```<label>```, and ```<input>``` elements
HTML5 validation via required and type="email"
No JavaScript used

## Accessibility Features

Semantic landmarks (header, main, section, article, aside, footer)
aria-label for navigation and sidebar
Proper alt attributes for images
Labels associated with form inputs
Logical heading hierarchy
Constraints Followed

## Learning Outcomes

Improved understanding of semantic HTML layout
Practical application of accessibility best practices
Experience building structured content without styling
Better comprehension of content hierarchy and navigation
