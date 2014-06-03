import codecs 


# template of html document
template_html = u'''
<!DOCTYPE html>
    <html>
        <head>
        <title>Konzertier</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
        <script>
        $(function() {
            $('.toggler').click(function() {
                $(this).find('div').slideToggle();
            });
        }); 
        </script>
        <style type="text/css">
        div.toggler { cursor:pointer; }
        div.toggler div { display:none; }
        td {
            vertical-align:top
        }
        #td1 {
            text-align:right
        }
        html *
        {
            font-size: 1em !important;
            color: #000 !important;
            font-family: Arial !important;
        }
        </style>
        </head>
        <body>
            %(body)s
        </body>
    </html>
    '''

# template of concert html block
template_entry = u'''
        <tr>
          <td>
            <table>
              <tr>
                <td><div class="toggler">%(artist)s</div></td>
              </tr>
              <tr>
                <td>%(venue_str)s</td>
              </tr>
              <tr>
                <td>%(date)s</td>
              </tr>
            </table>
          </td>   
          <td class="td1">    
            <a href="https://maps.google.com/?q=%(location_str)s">
              <img src="%(venue_image_url)s" width=120 alt="%(venue_image_url)s">
            </a>
          </td>   
        </tr>   
    '''

def make_html(concerts_dict, out_filename):
    '''create html document from concert dictionary'''
    entries = []
    sorted_concerts = sorted(concerts_dict.items(), key=lambda x: x[0])
    for k,v in sorted_concerts:
        for c in v:
            # create location string
            location_str_components = []
            location_list = [c.venue_name, c.street, c.city, c.postalcode, c.country]
            for n in location_list:
                if len(n) > 0:
                    location_str_components.append(n.replace(' ','%20'))
            location_str = u'+'.join(location_str_components)

            # create venue string
            venue_str = u''
            if c.title != c.artist['headliner']:
                venue_str = u'%s<br>' % c.title
            venue_str += c.venue_name

            venue_image_url = c.venue_image_url.replace(' ', '%20')
            if len(c.venue_image_url)==0:
                venue_image_url = u'http://seitel.com/PublishingImages/google%20map%20icon.jpg'

            # create artist string
            artist_str = '<b>'+c.artist_name+'</b>'
            if len(c.similar_artists) > 0:
                artist_str += u'<div>' + u'<br>'.join(c.similar_artists) + u'</div>'

            # fill entry template
            entry = template_entry % {
                'sim_band_height': 20*len(c.similar_artists),
                'artist': artist_str,
                'venue_str': venue_str,
                'location_str': location_str, 
                'date': c.date.strftime("%d.%m.%Y"),
                'venue_image_url': venue_image_url #c.venue_image_url.encode('utf8')
            }
            entries.append(entry)

    # create complete document
    body = u'<table>' + u'\n'.join(entries) + u'</table>'
    html_doc = template_html % {'body': body}

    # write document to file
    with codecs.open(out_filename, 'wb', 'utf8') as f:
        f.write(html_doc)
 
