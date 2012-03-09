# This Python file uses the following encoding: utf-8
import argparse, markdown, datetime, codecs, re, os, glob, time
from string import Template

# Set up command-line arguments
parser = argparse.ArgumentParser(description='Generate a blog from one or more Markdown files and an HTML template')
parser.add_argument('template', help='Template HTML')
args = parser.parse_args()

# Create a template string from the contents of the HTML template file 
t = codecs.open(args.template, 'r', 'utf-8')
template = Template(t.read())

root = os.path.dirname(os.path.abspath(__file__))

file_list = []

# Loop through all Markdown files in the current folder
for folder in glob.glob(root):
    # Select the type of file
    for f in glob.glob(folder + '/*.md'):
        # Retrieve the stats for the current file as a tuple
        # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        # mtime (index 9) is the file creation date
        stats = os.stat(f)
        # Create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
        # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
        created_date = time.localtime(stats[9])
        # Get the filename portion of the path
        markdown_file = os.path.split(f)[1]
        # Open the Markdown file and get the first line (heading)
        md = codecs.open(markdown_file, 'r', 'utf-8')
        heading = md.readline()
        # Replace the .md extension with .html
        html_file = re.sub(r"(?si)^(.*\.)(md)$", r"\1html", markdown_file)
        # Create a list of tuples containing post data, ready for sorting by date
        file_tuple = created_date, markdown_file, html_file, heading
        file_list.append(file_tuple)
 
# Sort by created date descending 
file_list.sort()
file_list.reverse()

nav_items = []

# Loop through all the files in the list and create a nav list item for each
for inputfile in file_list:
    # Add the item to nav (we are ordered by created date descending, so we're adding in the correct order)
    nav_item = u'<li><a href="' + inputfile[2] + '">' + inputfile[3][2:].strip() + '</a></li>'
    nav_items.append(nav_item)

nav = u'<ul>' + "".join(nav_items) + '</ul>'

# Collect the first n posts to display on the home page
homepage = []

for inputfile in file_list:
    # Read in the Markdown content
    c = codecs.open(inputfile[1], 'r', 'utf-8')
    content = c.read()
    # Get the creation date and insert into the template
    publishdate = datetime.datetime.fromtimestamp(time.mktime(inputfile[0]))
    contenttemplate = Template(content)
    content = contenttemplate.substitute(publishdate = publishdate.strftime("%d/%m/%Y %H:%M"))
    # If there are less than 5 posts in the homepage list, add this one
    if len(homepage) < 5: 
        homepage.append(content)
    # Process the Markdown content and put it into the template
    output = template.substitute(content = markdown.markdown(content), nav = nav)
    # Write out the processed HTML file
    o = codecs.open(inputfile[2], 'w', 'utf-8')
    o.write(output)

# Create the index page
output = template.substitute(content = markdown.markdown("\r\n".join(homepage)), nav = nav)
o = codecs.open('index.html', 'w', 'utf-8')
o.write(output)