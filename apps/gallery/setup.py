#-*- coding: utf8 -*-
from setuptools import setup


setup(
    name = 'gallery',
    version = '0.1.2.2',
    author = 'Adrian Lin',
    author_email = 'nildamului@gmail.com',
    packages = ['gallery'],
    package_dir = {
        'gallery': '.',
    },
    package_data = {
        'gallery': [
                'fixtures/*.json',
                'management/*.py',
                'management/commands/*.py',
                'migrations/*.py',
                'static/docx/*.docx',
                'static/gallery/apprise/*.*',
                'static/gallery/bootstrap3/css/*.*',
                'static/gallery/bootstrap3/fonts/*.*',
                'static/gallery/bootstrap3/js/*.*',
                'static/gallery/bootstrap-datetimepicker/*.*',
                'static/gallery/bootstrap-popover/css/*.*',
                'static/gallery/bootstrap-popover/js/*.*',
                'static/gallery/css/*.*',
                'static/gallery/images/*.*',
                'static/gallery/img/*.*',
                'static/gallery/img/numbers/*.*',
                'static/gallery/js/*.*',
                'static/gallery/jstree3/*.*',
                'static/gallery/jstree3/libs/*.*',
                'static/gallery/jstree3/themes/*.*',
                'static/gallery/jstree3/themes/default/*.*',
                'static/gallery/jstree3/themes/proton/*.*',
                'static/gallery/jstree3/themes/proton/fonts/titillium/*.*',
                'static/gallery/layout/*.*',
                'static/gallery/mcs/*.*',
                'static/gallery/plupload/*.js',
                'static/gallery/plupload/*.swf',
                'static/gallery/plupload/*.xap',
                'static/gallery/plupload/i18n/*.*',
                'static/gallery/plupload/jquery.plupload.queue/*.*',
                'static/gallery/plupload/jquery.plupload.queue/css/*.*',
                'static/gallery/plupload/jquery.plupload.queue/img/*.*',
                'static/gallery/plupload/jquery.ui.plupload/*.*',
                'static/gallery/plupload/jquery.ui.plupload/css/*.*',
                'static/gallery/plupload/jquery.ui.plupload/img/*.*',
                'static/gallery/portbox/*.*',
                'static/gallery/qtip/*.*',
                'static/gallery/smoothness/*.*',
                'static/gallery/smoothness/images/*.*',
                'static/gallery/webui-popover/*.*',
                'static/gallery/window/*.*',
                'static/gallery/window/css/*.*',
                'static/gallery/window/img/*.*',
                'templates/gallery/*.html',
                'templatetags/*.py',
        ],
    },
    url = 'http://bitbucket.org/nildamului/gallery',
    license = 'BSD licence, see LICENCE',
    description = '',
    long_description = open('README.rst').read(),
    platforms = ['any'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: ',
    ],
)