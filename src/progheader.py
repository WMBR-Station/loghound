"""
progheadergen produces the core piece of the programming logs: the headers for
each show that include the show name, engineer, announcer and producer.

running main is a good way to inspect the header's structure.  

header generation is in its own module because most of the tricky layout problems 
that can occur within the programming logs -- bad wrapping, truncation, 
pushing a column off the page, etc -- would happen here. 
                                            
to make sure those embarrassing problems don't happen to us, here's a few defenses:

* conservative truncation. if it remotely thinks the announcers won't fit,                
  for example, it'll leave the field blank and expect the dj to fill it                   
  in. this only happens in extreme cases.                                                 
                                                                                          
* font size reduction. the show title can't be truncated. so if it's really               
  long, it'll shrink the font size instead. this shouldn't happen often:                  
  show names can be 50 chars without triggering a font shrink.                            
                                                                                          
* tests. model.py has extreme cases of various shapes we can play                         
  with. feel free to add more.                                                                                                   
"""

# impl notes: tried using canvas.stringWidth(), 
# and two methods i found inside Paragraph's source: paragraph.minWidth(), 
# and [sic] paragraph.getActualLineWidths0()
#
# none of these gave good numbers on how wide 
# a paragraph is. so i decided to stop trying to manually measure and set 
# the column widths.
#
# instead it'll work like this: 
# 1. give a huge column width for the show title, 
# because show titles will often be long. 
#
# 2. in the rare event that the title is huge, 
# shrink the font to help it fit better. 
# 
# 3. give a small width for the engineer field, 
# that will accomodate a single long name. 
# if the name is too many characters, default
# to a blank engineer field that requires filling in. 
# super long engineer names are a tiny corner case -- 
# no reason to make a big deal out of it. 
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate
from reportlab.platypus import PageBreak, PageTemplate, Table
from reportlab.platypus import TableStyle, Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize

########### CONSTANTS

# widths for the show title column to the left and engineer column to the right
TITLE_COL_WIDTH = 4.4*inch 
ENGINEER_COL_WIDTH = 2.4*inch

# a larger fontsize is used for titles. 
# this makes line alignment a little tricky. these three parameters are
# tightly coupled. if the font changes, the title padding will probably need
# adjusting too. 
TITLE_FONTSIZE = 12 
TITLE_TOP_PADDING = 3.5
TITLE_BOTTOM_PADDING = 2

# how much to right-indent the engineer field when the engineer is blank. 
# (an rindent makes space for the engineer to write their name manually instead.)  
BLANK_ENGINEER_RINDENT = 70

#### max character widths: if any of the corresponding fields go beyond
#### these widths, they'll be truncated to blanks and the engineer will
#### need to write them in manually. this is to prevent crowding and wrapping --
#### a serious problem with the current logs. 
MAX_ANNOUNCER_WIDTH = 250
MAX_PRODUCER_WIDTH  = 250
MAX_ENGINEER_WIDTH  = 170
MAX_STUDIO_WIDTH  = 170
# note: max char bookkeeping is not the best way to go. max rendered widths
# would be better, as it's insenstive to changes in font and style.
# (see note above on challenges.)
# however, the log font sizes we use won't ever be changing radically, 
# so conservative character maxs should work just fine. 

# the show title is different: can't truncate it. instead, if it surpasses 
# this char length, i shrink the font.  
MAX_SHOW_CHARS = 50
FONT_SUBTRACTION = 2

# TODO: base or sample styles? or should we make our own?
STYLES=getSampleStyleSheet()

def make_header_table(show,alternates=False,freeblock=False):
    '''
    make_header_table takes a show as input and returns the header
    as a Table.    
    '''
        
    if len(show.name) >= MAX_SHOW_CHARS:
        # issue warning
        print "warning: this show's name might be too long: "+show.name

    def width(p):
        p.wrap(1e10,None)
        return sum(p.getActualLineWidths0())

    def truncate_if_needed(s, maxwidth, makeparagraph, singular_label, plural_label):
        # if something is too big to fit in the table,
        # return an empty string instead. 
        #
        # note: it'd be better to use the actual rendering
        # size than the character length. see note above:
        # i couldn't get it working for paragraphs.
        label = singular_label if len(s) == 1 else plural_label

        def make_text(s,n):

            if n == len(s) or len(s) == 1:
                return ", ".join(s)
            elif len(s) > 1:
                return ", ".join(s[:n]) + ' <i>et al</i>'

        if len(s) == 0:
            return makeparagraph(label,"")

        for offset in range(0,len(s)):
            n = len(s) - offset
            if width(makeparagraph(label,make_text(s,n))) <= maxwidth:
                return makeparagraph(label,make_text(s,n))

        raise Exception("could not fit in <%d> : <%s> [%d]" %
                        (maxwidth,make_text(s,len(s)),width(makeparagraph(label,make_text(s,len(s))))))
        #if width(makeparagraph(singular_label, s)) > maxwidth:
        #    i -= 1
        #    while i>0 and width(makeparagraph(singular_label, s[:i] + "...")) > maxwidth:
        #        i -= 1

	    #   if i == 0:
        #        return makeparagraph(singular_label, "")
        #
        #    return makeparagraph(singular_label, s[:i] + "...")

        #    return makeparagraph(singular_label, s)

        #else:
        #  i = 0

        #return [st for st in map(lambda i: makeparagraph(((i==1) and singular_label) or plural_label, ", ".join(s[:i] + ((i < len(s) and ["<i>et al</i>"]) or []))), xrange(len(s)+1)) if width(st) <= maxwidth][-1]
        
    def make_field(label, value, align='left'):
        if not value.strip():
            value = ''
            # this extra attr doesn't affect left-aligned fields.
            # it does affect the right-aligned engineer field: if the engineer
            # is blank, it'll rindent the field to make space for manual recording.
            extra_attrs = 'rindent="%s"' % BLANK_ENGINEER_RINDENT
        else:
            extra_attrs = ''
        text = '<para align=%s %s><i>%s:</i> %s</para>' % (align, extra_attrs, label, value)
        p = Paragraph(text, STYLES['Normal'])
        return p
    
    def make_note(label,align='left',extra_attrs=''):
        text = '<para align=%s %s>%s</para>' % (align, extra_attrs, label)
 	p = Paragraph(text, STYLES['Normal'])
        return p

    def make_title(name):
        if len(name) < MAX_SHOW_CHARS:
            fontsize = TITLE_FONTSIZE
        else:
            fontsize = TITLE_FONTSIZE-FONT_SUBTRACTION

        return Paragraph(
            '<para size="%d"><b>%s</b></para>' % (fontsize, name),
            STYLES['Normal'])

    if show.name == '':
        title = make_field('Title','',align='left')
    else:
        title = make_title(show.getXmlSafeName())

    engineer  = truncate_if_needed(show.engineer, MAX_ENGINEER_WIDTH,
                                   lambda l,v: make_field(l, v), "Engineer", "Engineers")
    producer  = truncate_if_needed(show.producer, MAX_PRODUCER_WIDTH,
                                   lambda l,v: make_field(l, v), "Producer", "Producers")
    announcer = truncate_if_needed(show.announcer, MAX_ANNOUNCER_WIDTH,
                                   lambda l,v: make_field(l, v), "Announcer", "Announcers")

    studio = make_field('Control Room','_'*7,align="left")

    freeblock_maybe = ''
    if freeblock:
       freeblock_maybe = make_note('<b>[unscheduled broadcast]</b>',align="right")
    elif alternates:
       freeblock_maybe = make_note('<b>[alternating show]</b>',align="right")

    data = [
        [title, freeblock_maybe],
        # these empty '' cells are required by reportlab's span mechanism
        [producer,engineer],
        [announcer,studio]
    ]
    
    tstyles = [
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),            
        ('TOPPADDING', (0,0), (-1,0), TITLE_TOP_PADDING),    
        ('BOTTOMPADDING', (0,0), (-1,0), TITLE_BOTTOM_PADDING),
        #('SPAN', (0,2), (1,2)),
        ('SPAN', (0,2), (0,2)),
        # comment-in the grid to get a better picture of the table structure
        #('GRID', (0,0), (-1,-1), .6, colors.black),                    
    ]
    
    cwidths = [TITLE_COL_WIDTH, ENGINEER_COL_WIDTH]
    rheights = [None, None, None] # 'None' means auto 
    return Table(data, cwidths, rheights, tstyles)


def main():
    import model
    doc = SimpleDocTemplate("prog_header_mockup.pdf")     
    story = [make_header_table(model.show5)]
    doc.build(story)

if __name__ == '__main__':
    pass
    #main()

