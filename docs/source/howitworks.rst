How does it work ?
==================

To be able to run Python on android, you need to compile it for android. And
you need to compile all the libraries you want for android too.
Since Python is a language, not a toolkit, you cannot draw any user interface
with it: you need to use a toolkit for it. Kivy can be one of them.

So for a simple ui project, the first step is to compile Python + Kivy + all
others libraries. Then you'll have what we call a "distribution".
A distribution is composed of:

- Python libraries
- All selected libraries (kivy, pygame, pil...)
- A java bootstrap
- A build script

You'll use the build script for create an "apk": an android package.

