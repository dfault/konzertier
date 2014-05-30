# template of html document
template_html = '''
    <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
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
    <html>
    '''

# template of concert html block
template_entry = '''
      <table>
        <td>
          <table>
            <tr>
              <td><b>%(artist)s</b></td>
            </tr>
            <tr>
              <td>%(venue_str)s</td>
            </tr>
            <tr>
              <td>%(date)s</td>
            </tr>
          </table>
        </td>   
        <td>    
          <a href="https://maps.google.com/?q=%(location_str)s">
            <img src="%(venue_image_url)s" height="80px">
          </a>
        </td>   
      </table>
    <br>
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
                    location_str_components.append(n.encode('utf8'))
            location_str = ' '.join(location_str_components)

            venue_str = ''
            if c.title != c.artist['headliner']:
                venue_str = '%s<br>' % c.title.encode('utf8')
            venue_str += c.venue_name.encode('utf8')

            venue_image_url = c.venue_image_url.encode('utf8')
            if len(c.venue_image_url)==0:
                venue_image_url = 'http://seitel.com/PublishingImages/google%20map%20icon.jpg'

            # fill entry template
            entry = template_entry % {
                'artist': c.artist_name, #c.artist['headliner'].encode('utf8'), 
                'venue_str': venue_str,
                'location_str': location_str, 
                'date': c.date.strftime("%d.%m.%Y"),
                'venue_image_url': venue_image_url #c.venue_image_url.encode('utf8')
            }
            entries.append(entry)

    # create complete document
    body = '<br>\n'.join(entries)
    html_doc = template_html % {'body': body}

    # write document to file
    with open(out_filename, 'wb') as f:
        f.write(html_doc)
 
