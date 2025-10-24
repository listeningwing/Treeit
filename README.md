# Treeit
Compare and merge big folders.

High performance duplicated file detector.<br>
High performance directory compare and merge.<br><br>

Find duplicates in big folders with lightning speed, visual diff tool on Mac, compare files and folders to see their differences and then side-by-side edit the modifications, and then merging the differences with selected flexible strategy on different files and folders.<br><br>

Essential tool for every software engineer. Version control system CAN'T DO AS YOUR EXPECTED! so this app developed. A small utility provides an intuitive and concise user interface to combine the content of two big folders. It accomplish the task in two steps with DIFFERENT algorithm that used by common version control systems, at the first step, the app scan the source and target folder to find out the difference, removed, new added, modified, conflicted file and folders, and at the same time, optionally check all duplicated items in both folder. At the second step, the app merge the compared result with user selected strategy. This practical tool can efficiently merge large amounts of media files such as photos, office documents, pdf files, audio and videos for normal users. Advanced users also can write scripts that cooperate with version control systems, e.g, Git and Mercurial, etc. In addition, of course, user also can directly use the app to generate coloured changes between two plain text file and print to pdf file or paper.


Features
===========================
a. Find duplicated files in the selected folder with high performance.<br>
b. Efficiently edit file side-by-side with compared result.<br>
c. Generate file list for removed, new added, duplicated, modified and conflicts in source and target folder with amazing speed.<br>
d. Pair modified, duplicated and conflicted source and target files together for conveniently review them before merging.<br>
e. Generate coloured changes between source and target file, line by line, character by character.<br>
f. Detect difference of binary files with content and file attributes when do comparing operation.<br>
g. Merging strategy includes: "always overwrite", "keeping the newest", and "keep both".<br>
h. Speed up comparing process by filter file, ignore particular folder and files by user defined rules.<br>
i. Export coloured PDF file by diff operation for file changes.<br>
...<br><br>


Compared Result Types
===========================
a. "+": this file or folder does not exist in target folder.<br>
b. "-": this file or folder does not exist in source folder.<br>
c. "O": can't do an overwrite operation, the file was conflicted with target file or folder.<br>
d. "M": this file was modified comparing with the target file.<br>
e. "R": this file should be renamed, it's conflicted with target file that has different content.<br>
f. "D": duplicated file in source or target folder.<br><br>


Sample Scenarios
===========================
a. There's a big folder in the external hard disk and a big folder in MacBook that contains large amounts of user's media files, user want to check out difference in both folder and merge the folder in MacBook into the external hard disk, but requires to apply a flexible strategy on different file and folder, and an intuitive interface to check each conflicted file and folder in all subfolders one by one before merging.

b. With the help of the app, software developers can fast find out and merge changes of a big project.


Scriptable App
===========================
The main functions of the app can be called from command line, user can call the interfaces with any scripting language, please refer the builtin sample file for details. As a fully programmable app, the app can generate the compared result as a json file, then user can filter records in the json file by scripting language, and then use the filtered new records for merging operation, such flexibility of design let user fully control what to compare and what to merge with scripting language in separated steps, in each step the main script can cooperate with any other scripts to deal with complex tasks.


AppStore Links
===============
https://apps.apple.com/us/app/treeit/id6468913170?mt=12<br>
https://apps.apple.com/us/app/treeit-lite/id6744892831<br>


Screenshots
===============

<img width="1440" height="900" alt="2025-08-21a" src="https://github.com/user-attachments/assets/599c494c-2747-4775-bee1-ce21e0151aff" />
<img width="1440" height="900" alt="2025-08-21b" src="https://github.com/user-attachments/assets/22c79f4e-8168-4b45-a450-23a84577b3b7" />

