"""
SecMapper: Section Mapping of Scientific Documents
using CRF and OCR'd by pdftoxml ( [dejean, giguet]@sourceforge.net )
Authors: Samuel Bushi, Rohith Kanuparthi
License: GNU GPLv3
"""

from __future__ import division

import xml.etree.ElementTree as ET
import unicodedata
import operator

import subprocess

import sys

import roman
import math

"""
Create an XML of headings and sections, Indexed type
"""


def generateXML(tree, filename):
    root = tree.getroot()
    chunk_list = root.findall('chunk')
    st_chunk = ''
    sp_length = len(chunk_list)
    chunk_stat = 0
    out_root = ET.Element("sec_map")
    new_section = ET.SubElement(out_root, "section")
    with open(filename, "r") as annot_file:
        count = 0
        for line in annot_file:
            cols = line.split('\t')
            if len(cols) == 9 and cols[8] == '1\n':
                st = ''
                for token in chunk_list[count].findall('token'):
                    st = st + token.text + ' '
                st = st.strip('\n')
                if chunk_stat == 1:
                    ET.SubElement(new_section, "chunk").text = st_chunk
                    chunk_stat = 0
                    st_chunk = ''
                new_section = ET.SubElement(out_root, "section")
                ET.SubElement(new_section, "heading").text = st
            elif count < sp_length:
                chunk_stat = 1
                for token in chunk_list[count].findall('token'):
                    st_chunk = st_chunk + token.text + ' '
                st_chunk = st_chunk.strip('\n')
            count += 1
    if chunk_stat == 1:
        ET.SubElement(new_section, "chunk").text = st_chunk
    return out_root


"""
Create an XML of headings and sections, Non-indexed type
"""


def generateXML_NI(tree, filename):
    root = tree.getroot()
    chunk_list = root.findall('chunk')
    st_chunk = ''
    sp_length = len(chunk_list)
    chunk_stat = 0
    out_root = ET.Element("sec_map")
    new_section = ET.SubElement(out_root, "section")
    with open(filename, "r") as annot_file:
        count = 0
        for line in annot_file:
            cols = line.split('\t')
            if len(cols) == 9 and cols[8] == '1\n':
                st = ''
                for token in chunk_list[count].findall('token'):
                    st = st + token.text + ' '
                st = st.strip('\n')
                if chunk_stat == 1:
                    ET.SubElement(new_section, "chunk").text = st_chunk
                    chunk_stat = 0
                    st_chunk = ''
                new_section = ET.SubElement(out_root, "section")
                ET.SubElement(new_section, "heading").text = st
            elif count < sp_length:
                chunk_stat = 1
                for token in chunk_list[count].findall('token'):
                    st_chunk = st_chunk + token.text + ' '
                st_chunk = st_chunk.strip('\n')
            count += 1
    if chunk_stat == 1:
        ET.SubElement(new_section, "chunk").text = st_chunk
    return out_root


"""
Token features as decimals
Special Sections    - 6
Single word chunk   - 5
Tables/Figures      - 0
Section Number      - 1
UpperCase token     - 2
Special Symbols     - 3
Rest                - 4
"""


def token_features(tok_input):
    tok = tok_input.strip()
    parts = tok.split('.')
    # Mark special sections
    if tok == "Abstract" or tok == "ABSTRACT" or tok == "Acknowledgement" or tok == "ACKNOWLEDGEMENT" or tok == "References" or tok == "Reference" or tok == "REFERENCE" or tok == "REFERENCES" or tok == "Acknowledgements" or tok == "ACKNOWLEDGEMENTs":
        return "6"
    # Mark special symbol '$$$'
    if tok == "$$$":
        return "5"
    # Mark table/figure headings
    if tok == "Table" or tok == "TABLE" or tok == "Figure" or tok == "FIGURE" or tok == "Fig.":
        return "0"
    p_len = len(parts)
    # Digit tokens
    if p_len == 1:
        if tok.isdigit() and 1 <= int(tok) <= 20:
            return "1"
    if p_len == 2 or p_len == 3:
        if parts[0].isdigit() and 1 <= int(parts[0]) <= 20:
            if parts[1] == '' or (parts[1].isdigit() and int(parts[1]) <= 20):
                if p_len == 2:
                    return "1"
                if parts[1].isdigit() and int(parts[1]) <= 20 and parts[2] == '':
                    return "1"
    # Handling Roman Numericals
    if p_len == 1 or (p_len == 2 and parts[1] == ''):
        try:
            val = roman.fromRoman(parts[0].upper())
            if val <= 20:
                return "1"
        except:
            pass
        if ((len(parts[0]) == 1 and 'A' <= parts[0] <= 'Z') or (
                            len(parts[0]) == 3 and parts[0][0] == '(' and parts[0][2] == ')' and parts[0][
                1].isalpha() and parts[0][1].isupper()) or (
                                len(parts[0]) == 2 and parts[0][1] == ')' and parts[0][0].isalpha() and parts[0][
                    0].isupper())):
            if p_len == 1 or (p_len == 2 and parts[1] == ''):
                return "1"
    # Handling Capitalizations
    if tok[0].isupper():
        return "2"
    if not (parts[0].isalpha() or parts[0].isdigit()):
        return "3"
    return "4"


"""
Main function for section mapping
includes the pdftoxml file and the Path to the
file as parameters, path is defaulted to be the
current directory
"""


def secmap(input_xml, path=""):
    if path is "":
        tree = ET.parse(input_xml)
    else:
        if path.endswith("/"):
            tree = ET.parse(path+input_xml)
        else:
            tree = ET.parse(path+"/"+input_xml)

    output_prefix = input_xml.split('/')[-1].split('.')[0]
    root = tree.getroot()

    preYLOC = None
    yDiff = {}
    fontSizes = {}

    # Initial pass to gather the differences in y values
    # And font size info
    for pages in root.findall('PAGE'):
        preYLOC = 0
        for texts in pages.findall('TEXT'):
            for token in texts.findall('TOKEN'):
                try:
                    fontSizes[round(abs(float(token.attrib['font-size'])))] = fontSizes.get(
                        round(abs(float(token.attrib['font-size']))), 0) + 1
                    if (preYLOC is None):
                        preYLOC = float(token.attrib['y'])
                    yDiff[round(abs(float(token.attrib['y']) - preYLOC))] = yDiff.get(
                        round(abs(float(token.attrib['y']) - preYLOC)), 0) + 1
                    preYLOC = float(token.attrib['y'])
                except:
                    pass

    modalFS = 0
    # Find Modal Font size
    for FS in fontSizes.keys():
        if modalFS == 0:
            modalFS = FS
            continue
        if fontSizes[FS] > fontSizes[modalFS]:
            modalFS = FS

    # The following few lines may not be very lucid. But the basic gist is to extract a 
    # plausible threshold for chunking two lines, by using the mode of Y differences.

    # Finding modal Y difference
    top_Ydiff = sorted(yDiff.iteritems(), key=operator.itemgetter(1), reverse=True)[:7]
    ref_YTop = []

    # Select only those whose Ydiff is more than 6 (Say)
    for Y in top_Ydiff:
        if Y[0] > 6.0:
            ref_YTop.append(Y)

    top_Ydiff = ref_YTop
    ref_YTop = []
    # Modal y_diff
    mode = top_Ydiff[0][1]
    for Y in top_Ydiff:
        if not (Y[1] <= mode / 2 or abs(top_Ydiff[0][0] - Y[0]) >= 4):
            ref_YTop.append(Y)

    top_Ydiff = ref_YTop

    del ref_YTop

    # Threshold of max_Y_diff to chunk
    limit = max([x[0] for x in top_Ydiff]) + 1

    # Create temp XML file for Chunks

    preYLOC = None
    temp_root = ET.Element("Document")
    chunk = ET.SubElement(temp_root, "chunk")
    for pages in root.findall('PAGE'):
        for texts in pages.findall('TEXT'):
            for token in texts.findall('TOKEN'):
                # Handling special characters from Unicode
                if type(token.text) is unicode:
                    word = unicodedata.normalize('NFKD', token.text).encode('ascii', 'ignore')
                else:
                    word = token.text
                if word and len(word.replace(' ', '')) > 0:
                    # Add token tag to chunk
                    if (preYLOC is None):
                        preYLOC = float(token.attrib['y'])
                        ET.SubElement(chunk, "token", font_size=token.attrib['font-size'],
                                      bold=token.attrib['bold']).text = word
                        continue
                    if abs(float(token.attrib['y']) - preYLOC) >= limit:
                        chunk = ET.SubElement(temp_root, "chunk")
                    preYLOC = float(token.attrib['y'])
                    ET.SubElement(chunk, "token", font_size=token.attrib['font-size'],
                                  bold=token.attrib['bold']).text = word

    tree = ET.ElementTree(temp_root)

    # Save the tree as tree_NI
    tree_NI = tree

    temp_root2 = ET.Element("Document")
    ET.SubElement(temp_root2, "chunk")

    preFS = None

    root = tree.getroot()

    # Refining chunks to strip leading headings
    # By re-chunking sufficiently large chunks based on
    # a small font prefix string
    # For INDEXED Documents

    for chunks in root.findall('chunk'):
        chunk = ET.SubElement(temp_root2, "chunk")
        count = 0
        stat = 0
        if len(chunks) > 20:
            stat = 1
        for token in chunks.findall('token'):
            # Small === 15 in size
            if count < 15 and preFS is not None and float(token.attrib["font_size"]) < preFS and stat == 1:
                chunk = ET.SubElement(temp_root2, "chunk")
                ET.SubElement(chunk, "token", font_size=token.attrib['font_size'],
                              bold=token.attrib['bold']).text = token.text
            else:
                ET.SubElement(chunk, "token", font_size=token.attrib['font_size'],
                              bold=token.attrib['bold']).text = token.text
                count += 1
            preFS = float(token.attrib['font_size'])

    tree = ET.ElementTree(temp_root2)

    temp_root2 = ET.Element("Document")
    ET.SubElement(temp_root2, "chunk")

    # Repeating the same for NI documents
    root = tree_NI.getroot()
    preFS = None
    for chunks in root.findall('chunk'):
        chunk = ET.SubElement(temp_root2, "chunk")
        count = 0
        stat = 0
        if len(chunks) > 20:
            stat = 1
        for token in chunks.findall('token'):
            if count < 15 and preFS is not None and preFS < float(token.attrib["font_size"]) and stat == 1:
                chunk = ET.SubElement(temp_root2, "chunk")
                ET.SubElement(chunk, "token", font_size=token.attrib['font_size'],
                              bold=token.attrib['bold']).text = token.text
            else:
                ET.SubElement(chunk, "token", font_size=token.attrib['font_size'],
                              bold=token.attrib['bold']).text = token.text
                count += 1
            preFS = float(token.attrib['font_size'])

    tree_NI = ET.ElementTree(temp_root2)

    # Generating the final txt config file

    feature_file = open(output_prefix + '_out.txt', 'w')

    temp_root2 = tree.getroot()

    for chunk in temp_root2.findall('chunk'):
        boldness = 0
        fsize = 0
        tokens = chunk.findall('token')
        if len(tokens) == 0:
            # Empty chunk workaround
            # Empty chunks are needed to maintain the same mapping for post-processing
            feature_file.write('xxx\t0\t0\t0.0\t0\t0\t0\t0\n')
            continue
        elif len(tokens) == 1:
            # Chunk having only one token
            tok1 = '$$$'
            tok2 = tokens[0].text
        else:
            # Chunks with >= 2 tokens
            tok1 = tokens[0].text
            tok2 = tokens[1].text
        tok_count = len(tokens)
        # Finding average boldness in chunk
        for t in tokens:
            if t.attrib['bold'] == "yes":
                boldness += 1
            fsize += float(t.attrib['font_size'])
        boldness = round(boldness / tok_count, 2)
        # Relative font-size of tokens in chunk
        fsize = (fsize / tok_count) / modalFS
        # Size of chunk taken in steps of 16
        tok_count = math.floor(tok_count / 16)
        feature_file.write(tok1 + "\t" + tok2 + "\t" + str(int(tok_count)) + "\t" + str(boldness) + "\t" + str(
            round(fsize, 2)) + "\t" + token_features(tok1) + "\t" + token_features(tok2) + "\t0\n")

    feature_file.close()
    # Run the CRF model here, assumed that it is already present/accessible in the system path
    # Otherwise, the feature_file can be used to manually run the CRF
    subprocess.call(
        "crf_test -m mod_i " + output_prefix + '_out.txt' + " > " + output_prefix + "_finalsec.txt",
        shell=True)

    # Feature file for NI Documents
    feature_file = open(output_prefix + '_out_NI.txt', 'w')
    temp_root2 = tree_NI.getroot()

    for chunk in temp_root2.findall('chunk'):
        boldness = 0
        fsize = 0
        tokens = chunk.findall('token')
        if len(tokens) == 0:
            feature_file.write('xxx\t0\t0\t0.0\t0\t0\t0\t0\n')
            continue
        elif len(tokens) == 1:
            tok1 = '$$$'
            tok2 = tokens[0].text
        else:
            tok1 = tokens[0].text
            tok2 = tokens[1].text
        tok_count = len(tokens)
        for t in tokens:
            if t.attrib['bold'] == "yes":
                boldness += 1
            fsize += float(t.attrib['font_size'])
        boldness = round(boldness / tok_count, 2)
        fsize = (fsize / tok_count) / modalFS
        tok_count = math.floor(tok_count / 16)
        feature_file.write(tok1 + "\t" + tok2 + "\t" + str(int(tok_count)) + "\t" + str(boldness) + "\t" + str(
            round(fsize, 2)) + "\t" + token_features(tok1) + "\t" + token_features(tok2) + "\t0\n")

    feature_file.close()

    # Run CRF on NI feature file
    subprocess.call("crf_test -m mod_ni " + output_prefix + '_out.txt' + " > " + output_prefix + "_finalsec_NI.txt",
                    shell=True)

    # Respective XMLs generated
    secTree_I = generateXML(tree, output_prefix + "_finalsec.txt")
    secTree_NI = generateXML_NI(tree, output_prefix + "_finalsec_NI.txt")

    # List of most common Conference/Journals to strip from the output
    journal_related = ["ACM", "Elsevier", "ELSEVIER", "arxiv", "ARXIV", "IEEE", "ieee", "CONFERENCE", "INTERNATIONAL",
                       "R E S E A R C H", "RESEARCH", "DETECTION", "Open"]

    temp_root = ET.Element("sec_map")

    # Pretty format into XML, the output
    for section in secTree_I.findall('section'):
        new_stat = 0
        new_head = 0
        new_section = ET.SubElement(temp_root, "section")
        for heading in section.findall('heading'):
            new_head = 1
            if len(heading.text.split()) <= 10:
                # Check if its not in the journal_list
                for x in journal_related:
                    if x in heading.text:
                        for chunk in section.findall("chunk"):
                            ET.SubElement(new_section, "chunk").text = (heading.text + " " + chunk.text)
                        new_stat = 1
                        break
                if new_stat == 0:
                    ET.SubElement(new_section, "heading").text = heading.text
                    for chunk in section.findall('chunk'):
                        ET.SubElement(new_section, 'chunk').text = chunk.text
            else:
                for chunk in section.findall("chunk"):
                    ET.SubElement(new_section, "chunk").text = (heading.text + " " + chunk.text)
        if new_head == 0:
            for chunk in section.findall('chunk'):
                ET.SubElement(new_section, 'chunk').text = chunk.text

    tree_I = ET.ElementTree(temp_root)

    temproot_NI = ET.Element("sec_map")

    for section in secTree_NI.findall('section'):
        new_stat = 0
        new_head = 0
        new_section = ET.SubElement(temproot_NI, "section")
        for heading in section.findall('heading'):
            new_head = 1
            if len(heading.text.split()) <= 10:
                for x in journal_related:
                    if x in heading.text:
                        for chunk in section.findall("chunk"):
                            ET.SubElement(new_section, "chunk").text = (heading.text + " " + chunk.text)
                        new_stat = 1
                        break
                if new_stat == 0:
                    ET.SubElement(new_section, "heading").text = heading.text
                    for chunk in section.findall('chunk'):
                        ET.SubElement(new_section, 'chunk').text = chunk.text
            else:
                for chunk in section.findall("chunk"):
                    ET.SubElement(new_section, "chunk").text = (heading.text + " " + chunk.text)
        if new_head == 0:
            for chunk in section.findall('chunk'):
                ET.SubElement(new_section, 'chunk').text = chunk.text

    tree_NI = ET.ElementTree(temproot_NI)

    # Finalizing the one with more headings
    count_I = 0
    count_NI = 0
    for section in tree_I.findall("section"):
        count_I += len(section.findall("heading"))
    for section in tree_NI.findall("section"):
        count_NI += len(section.findall("heading"))
    if count_I >= count_NI:
        print "Indexed!"
        tree_I.write(output_prefix + "_secmap.xml")
        subprocess.call("rm "+output_prefix+"_finalsec_NI.txt ", shell=True)
    if count_I < count_NI:
        print "Non-Indexed!"
        tree_NI.write(output_prefix + "_secmap.xml")
        subprocess.call("rm "+output_prefix+"_finalsec.txt ", shell=True)

    subprocess.call("rm "+output_prefix+"_out.txt "+output_prefix+"_out_NI.txt", shell=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python ", sys.argv[0], " [XML_FILE_NAME] [PATH]"
        exit(1)
    else:
        if len(sys.argv) == 2:
            secmap(sys.argv[1])
        if len(sys.argv) == 3:
            if sys.argv[1].endswith(".xml"):
                secmap(sys.argv[1], sys.argv[2])
            else:
                secmap(sys.argv[2], sys.argv[1])