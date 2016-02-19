# SecMapper

SecMapper: Section Mapping of Scientific Documents (PDFs)
using CRF and OCR'd by [pdftoxml][1].


## Prerequisites

####  pdf2xml:

1. Download `pdf2xml` from [here][1].
2. Extract and make executable `chmod +x pdf2xmlexecutable`
3. Optional: Move it to  `/usr/local/bin/`

   `sudo mv pdftoxmlexecutable /usr/local/bin/pdftoxml`

####  CRF++:

Download CRF++ from [here][2]. Follow the instructions in the INSTALL file/ in the website. You might have to run `ldconfig` at the end to update your libraries. Run `$ crf_learn` to check if the installation is complete.



## Usage

Secmapper takes input the XML file generated by `pdftoxml` and produces the mapped sections in another XML file. Besides the final XML, one file is generated which contains the raw section features annotated by the CRF. This is done to expose the inner working and improve the model.

**Instructions:**
1. Run `pdftoxml` on the pdf: `pdftoxml mypdf.pdf rawxml.xml`
   or `/path/to/pdftoxmlexecutable mypdf.pdf rawxml.xml`. Make sure that `pdftoxml` is executable
2. Use the SecMapper.py script:
  * `python SecMapper.py rawxml.xml`
  * `python SecMapper.py /path/to/rawxml.xml`
  * You can also give the path explicitly by `python SecMapper.py rawxml.xml /path/to/the/rawxml`. Useful for batch processing.
3. Thats it! The output is generated in the current directory (where SecMapper.py is present with the name `rawxml_secmap.xml`).

## Contributing

I have also included the necessary files which can be guidelines to improving the model. Templates for crf_learn, sample training data have been provided. More info on how to use CRF++ can be found at its [homepage][2].

Contribute to this tool by:

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Notes:

SecMapper is a promising tool to extract sections and headings from scientific documents.  The PDF is first segmented into regions or *chunks*, by means of its distance from neighboring text and a measure of how different it is from the surrounding text, in terms of font-size and bold-text(*makes more sense when you look into the code*).

It runs on 2 seperate models, one for pdfs with Numerical indices for headings like most papers in ACM, IEEE, etc. And the other for pdfs without indices, like CHI.

Its key strength lies here that each model can thus be tuned to its one fineness, without affecting the other, maximizing the accuracy.

Unfortunately, we have only managed to manually annotate and train on around 20 pdfs, but tested it on more than 100 pdfs. The results were about **77% in F-Score (overall).** 

It is therefore expected that increase in training data will provide *far better* results.

## Credits

**Authors:**
   * [Samuel Suraj Bushi][3]
   * [Krishna Sai Rohith Kanuparthi][4]

## License

**GNU GENERAL PUBLIC LICENSE v3.**

See the LICENSE file for more details.

[1]: https://sourceforge.net/projects/pdf2xml/
[2]: https://taku910.github.io/crfpp/#download
[3]: mailto:samuelsbushi@gmail.com
[4]: mailto:krishnasai.rohith07@gmail.com