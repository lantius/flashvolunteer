import os, os.path, shutil

#### CODE DERIVED FROM http://stackoverflow.com/questions/1199470/combine-javascript-files-at-deployment-in-python


import utils
path = os.path.dirname(utils.__file__)


YUI_COMPRESSOR = os.path.join(path,'yuicompressor-2.4.2.jar')

stylesheets = os.path.join(path,'..','stylesheets')


def compress(in_files, out_file, in_type='js', verbose=False,
             temp_file='.temp'):
    temp = open(temp_file, 'w')
    for f in in_files:
        fh = open(f)
        data = fh.read() + '\n'
        fh.close()

        temp.write(data)

        print ' + %s' % f
    temp.close()

    options = ['-o "%s"' % out_file,
               '--type %s' % in_type]

    if verbose:
        options.append('-v')

    os.system('java -jar "%s" %s "%s"' % (YUI_COMPRESSOR,
                                          ' '.join(options),
                                          temp_file))

    org_size = os.path.getsize(temp_file)
    new_size = os.path.getsize(out_file)

    print '=> %s' % out_file
    print 'Original: %.2f kB' % (org_size / 1024.0)
    print 'Compressed: %.2f kB' % (new_size / 1024.0)
    print 'Reduction: %.1f%%' % (float(org_size - new_size) / org_size * 100)
    print ''

SCRIPTS = [
    os.path.join(stylesheets, 'javascript', 'dialog_box.js'),
    os.path.join(stylesheets, 'javascript', 'mtaTwitterStatuses.js'),
    os.path.join(stylesheets, 'javascript', 'misc.js'),

    os.path.join(stylesheets, 'jquery', 'js', 'jquery-1.3.2.min.js'),
    os.path.join(stylesheets, 'jquery', 'js', 'jquery-ui-1.7.2.custom.min.js'),
    
    os.path.join(stylesheets, 'json', 'json2.min.js'),
    
    os.path.join(stylesheets, 'javascript', 'jquery.address-1.0.js'),
    os.path.join(stylesheets, 'javascript', 'load_page_info.js'),
    os.path.join(stylesheets, 'javascript', 'misc_ajax.js'),

#    os.path.join(stylesheets, 'jquery.ezjax.js'),
    
    ]    
    
SCRIPTS_OUT_DEBUG = os.path.join(stylesheets, 'javascript', 'fv.js')

SCRIPTS_OUT = os.path.join(stylesheets, 'javascript', 'fv.min.js')


STYLESHEETS = [
    os.path.join(stylesheets, 'css', 'reset-min.css'),
    os.path.join(stylesheets, 'jquery', 'css', 'flashvolunteer', 'jquery-ui-1.7.2.custom.css'),
    os.path.join(stylesheets, 'css', 'main.css'),
    os.path.join(stylesheets, 'css', 'layout.css'),
    os.path.join(stylesheets, 'css', 'colors_backgrounds_borders.css'),
    os.path.join(stylesheets, 'css', 'create_event.css'),
    os.path.join(stylesheets, 'css', 'event_photos.css'),
]

STYLESHEETS_OUT =  os.path.join(stylesheets, 'css', 'fv.min.css')

def main():
    print 'Compressing JavaScript...'
    compress(SCRIPTS, SCRIPTS_OUT, 'js', False, SCRIPTS_OUT_DEBUG)

    print 'Compressing CSS...'
    compress(STYLESHEETS, STYLESHEETS_OUT, 'css')

if __name__ == '__main__':
    main()
