"""
 * Copyright 2023 Francois Cartegnie
 *
 * Licensed under the DontBugMe License, Version 1.0;
 * you may not use this file except in compliance with the License.
 * The Software is provided "as is", without warranty of any kind, express
 * or implied, including but not limited to the warranties of merchantability,
 * fitness for a particular purpose and noninfringement
 * If you don't agree with those terms and complain to author about functionalities,
 * you are then required to share ten percent of your salary with me on the month of
 * your complain and go dance naked on the main street of your city with a large
 * cardboard stating you do not read software licenses before usage.
 *
"""

import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab_qrcode import QRCodeImage
#from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import argparse

csvkeymap = { 'type': 'Type of Participant',
              'email': 'Email',
              'lastname': 'Last Name',
              'firstname': 'First Name',
              'role': 'Job Title',
              'company': 'Organisation' }

knownlayouts = {
     '4278' : { 'page': A4,
                'card': (70, 50.8),
                'rows': 5,
                'cols': 3,
                'padding': (0, 0),
                'borders': ((A4[0] - 3 * 70*mm) / 2, (A4[1] - 5 * 50.8*mm) / 2),
                'desc': "HERMA Premium White Labels 70 x 50.8mm" },
     '4668' : { 'page': A4,
                'card': (70, 42.3),
                'rows': 7,
                'cols': 3,
                'padding': (0, 0),
                'borders': ((A4[0] - 3 * 70*mm) / 2, (A4[1] - 5 * 42.3*mm) / 2),
                'desc': "HERMA Premium White Labels 70 x 42.3mm" },
     '1212' : { 'page': A4,
                'card': (70, 37),
                'rows': 8,
                'cols': 3,
                'padding': (0, 0),
                'borders': ((A4[0] - 3 * 70*mm) / 2, (A4[1] - 8 * 37*mm) / 2),
                'desc': "APLI White Labels 70 x 37mm" },
}

def make_vcard(
        first_name,
        last_name,
        company,
        email):
    return '\r\n'.join([
        'BEGIN:VCARD',
        'VERSION:2.1',
        f'N:{last_name};{first_name}',
        f'ORG:{company}',
        f'EMAIL:{email}',
        'END:VCARD'
    ])


class BadgeMaker:
    entries = []
    layout = None
    debug = False
    
    def __init__(self, layout):
        self.layout = layout
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        pdfmetrics.registerFont(TTFont('VeraBold', 'VeraBd.ttf'))
        pass

    def open_csv(self, filename, csvrange):
        first = 0 if csvrange[0] == None else csvrange[0]
        last  = 2147483647 if csvrange[1] == None else csvrange[1]
        with open(filename, "r") as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')
            idx = 0
            for row in reader:
                if len(row) and idx >= first and idx <= last:
                    self.entries.append(row)
                idx = idx + 1

    def fit_text(self, text, fontname, fontsize, width, height):
        while True:
            w = pdfmetrics.stringWidth( text, fontname, fontsize )
            face = pdfmetrics.getFont(fontname).face
            h = (face.ascent - face.descent) / 2000 * fontsize
            if w < width or fontsize <= 0.5:
                return [ fontsize, w, h ]
            fontsize -= 0.5
            

    def fill_badge(self, c, x, y, width, height, entry):
        if self.debug:
            c.rect(x, y, width, height, stroke=1, fill=0)
        
        padding = 3 * mm
        x += padding / 2
        y += padding / 2
        width -= padding
        height -= padding
        qrcodesize = height * 0.35
       
        # Draw the box with the name, surname, and email
        #c.rect(x, y, width, height, stroke=1, fill=0) # padded zone

        if len(entry[csvkeymap['type']]): # badge type
            c.saveState()
            # c.roundRect(x, y + height - height * 0.15, width, height * 0.15, 1*mm, stroke=1, fill=1)
            # c.setFillColor(HexColor(0xffffff))
            metrics = self.fit_text( entry[csvkeymap['type']].upper(), 'Vera', 16, width, height * 0.15 )
            c.setFont('Vera', metrics[0])
            c.drawString(x, y + height - height * 0.075 - metrics[2], entry[csvkeymap['type']].upper())
            c.restoreState()

        c.line(x, y + height - height * 0.25, x + 0.95 * (width - qrcodesize), y + height - height * 0.25 )

        # names
        c.saveState()
        posy = y + height - height * 0.35 - 5 * mm
        fullname = entry[csvkeymap['firstname']] + " " + entry[csvkeymap['lastname']];
        print("Generating badge for: ", fullname)
        metrics = self.fit_text( fullname, 'VeraBold', 22, width, height * 0.20 )
        if metrics[0] >= 16:
            posy -= metrics[2]
            c.setFont('VeraBold', metrics[0])
            c.drawString(x, posy, fullname)
        else:
            posy = y + height - height * 0.20 - 5 * mm
            metricsA = self.fit_text( entry[csvkeymap['firstname']], 'VeraBold', 22, width, height * 0.20 )
            metricsB = self.fit_text( entry[csvkeymap['lastname']], 'VeraBold', 22, width, height * 0.20 )
            metrics = metricsA if metricsA[0] <= metricsB[0] else metricsB
            posy -= metrics[2]
            c.setFont('VeraBold', metrics[0])
            c.drawString(x, posy, entry[csvkeymap['firstname']])
            posy -= metrics[2] + 5 * mm
            c.setFont('VeraBold', metrics[0])
            c.drawString(x, posy, entry[csvkeymap['lastname']])        
        c.restoreState()

        # company 
        c.saveState()
        metrics = self.fit_text( entry[csvkeymap['role']], 'Vera', 16, width - qrcodesize, height * 0.20 )
        posy -= metrics[2] + 5*mm
        c.setFont('Vera', metrics[0])
        c.drawString(x, posy, entry[csvkeymap['role']])
        metrics = self.fit_text( entry[csvkeymap['company']], 'Vera', 16, width - qrcodesize, height * 0.20 )
        posy -= metrics[2] + 5*mm
        c.setFont('Vera', metrics[0])
        c.drawString(x, posy, entry[csvkeymap['company']])
        c.restoreState()

        qrdata = make_vcard(entry[csvkeymap['firstname']],
                            entry[csvkeymap['lastname']],
                            entry[csvkeymap['company']],
                            entry[csvkeymap['email']])
        qr = QRCodeImage(qrdata, size=qrcodesize, border=1*mm)
        qr.drawOn(c, x + width - qrcodesize, y + height - qrcodesize)

    # Function to generate the PDF file
    def generate_pdf(self, outputfile, badgeindex):

        papertype = self.layout['page']
        pagewidth, pageheight = papertype
        
        badge_width = self.layout['card'][0] * mm
        badge_height = self.layout['card'][1] * mm
        columns = self.layout['cols']
        rows = self.layout['rows']

        borderleft = self.layout['borders'][0]
        borderbottom = self.layout['borders'][1]

        interx = self.layout['padding'][0]
        intery = self.layout['padding'][1]

        c = canvas.Canvas(outputfile, pagesize=papertype)

        if self.debug:
            c.rect(0, 0, pagewidth, pageheight, stroke=1, fill=0)

        for i, entry in enumerate(self.entries):
            # Calculate the position of the box based on the box size and grid size
            x = borderleft + (badgeindex % columns) * badge_width
            y = borderbottom + (badgeindex // columns) % (rows) * badge_height

            if interx:
                x = x + (badgeindex % columns) * interx
            if intery:
                y = y + ((badgeindex % (rows*columns)) // columns) * intery

            entry['row'] = i
            self.fill_badge(c, x, y, badge_width, badge_height, entry)
            
            # Create a new page for each grid
            if (i+1) % (rows*columns) == 0:
                c.showPage()

            badgeindex = badgeindex + 1

        c.showPage()
        c.save()
                
    # Function to start the GUI
    def run(self, inputfile, outputfile, start, csvrange):
        self.open_csv(inputfile, csvrange)
        self.generate_pdf(outputfile, start)

    def set_debug(self):
        self.debug = True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", default=knownlayouts['1212'])
    parser.add_argument("--debug", action='store_true', help="print with layout debugging marks")
    parser.add_argument("--layout-list", action="store_true", help="display supported layouts")
    parser.add_argument("--start", type=int, help="start number of layout sticker", default=0)
    parser.add_argument("--csvfirst", type=int, help="csv entries first index to process")
    parser.add_argument("--csvlast", type=int, help="csv entries last index to process")
    parser.add_argument("input.csv", nargs='?')
    parser.add_argument("output.pdf", nargs='?')
    args = parser.parse_args()
    if args.layout_list:
        for k, v in knownlayouts.items():
            print(k , " ", v['desc'])
        exit(0)
    elif not getattr(args, 'input.csv'):
        print("missing input file")
        exit(1)
    elif not getattr(args, 'output.pdf'):
        print("missing output file")
        print(args)
        exit(1)
    else:
        badge_maker = BadgeMaker(args.layout)
        if args.debug:
            badge_maker.set_debug()
        badge_maker.run(getattr(args, 'input.csv'), getattr(args, 'output.pdf'), args.start, (args.csvfirst, args.csvlast))
        exit(0)
    pass

if __name__ == "__main__":
    main()


