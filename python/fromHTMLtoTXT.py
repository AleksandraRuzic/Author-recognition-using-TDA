from bs4 import BeautifulSoup
import os


# Parses html to a txt file (removes most of tags, titles...) returning raw text
# Works for most books, some need to be manualy cleaned
def parseHTML(filename):

    file = open("../html_books_2/" + filename, "r", encoding="utf8")

    file = file.read()

    soup = BeautifulSoup(file, 'html.parser')

    tg = soup.find_all(attrs={"class": "tei tei-front"})
    if len(tg) >= 1:
        tg[0].replace_with("")

    tg = soup.find_all(attrs={"h3", "tei tei-head"})

    for x in tg:
        x.replace_with("")

    tg = soup.find_all(attrs={"span", "tei tei-pb"})

    for x in tg:
        x.replace_with("")

    tg = soup.find_all(attrs={"class": "tei tei-back"})
    if len(tg) >= 1:
        tg[0].replace_with("")


    tg = soup.find_all(["pre"])
    if len(tg) >= 2:
        tg[0].replace_with("")
        tg[-1].replace_with("")

    soup.title.clear()

    tg = soup.find_all(attrs={"class": "pageno"})
    for x in tg:
        x.replace_with("")

    tg = soup.find_all(attrs={"p", "toc"})
    for x in tg:
        x.replace_with("")

    tg = soup.find_all(attrs={"span", "pagenum"})
    for x in tg:
        x.replace_with("")

    tg = soup.find_all(attrs={"p", "centered"})
    for x in tg:
        x.replace_with("")

    tg = soup.find_all(["h1", "h2", "h3", "h4", "h5", "table"])
    for x in tg:
        x.replace_with("")

    text = soup.get_text()

    text = text.strip()

    new_filename = "../books_2/" + '.'.join(filename.split('.')[:-1]) + ".txt"
    os.makedirs(os.path.dirname(new_filename), exist_ok=True)
    file2 = open(new_filename, "w", encoding="utf8")
    file2.write(text)


directory = "../html_books_2"

# Loop through all files in folder html_books
for filename in os.listdir(directory):
    #if filename.endswith(".html") or filename.endswith(".htm"):
    if filename == "FyodorDostoyevski_StavroginsConfession.htm":
        parseHTML(filename)
