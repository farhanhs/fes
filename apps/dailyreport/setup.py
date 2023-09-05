#-*- coding: utf8 -*-
from setuptools import setup


setup(
    name='dailyreport',
    version='1.0.0',
    packages = ['dailyreport'],
    package_dir={
        'dailyreport': '.',
    },
    package_data={
        'dailyreport': [
                'fixtures/*.json',
                'migrations/*.py',
                'static/dailyreport/*.*',
                'static/dailyreport/bootstrap/css/*.*',
                'static/dailyreport/bootstrap/img/*.*',
                'static/dailyreport/bootstrap/js/*.*',
                'static/dailyreport/css/*.*',
                'static/dailyreport/images/*.*',
                'static/dailyreport/images/explanation_image/*.*',
                'static/dailyreport/jquery/*.*',
                'static/dailyreport/jquery/smoothness/*.*',
                'static/dailyreport/jquery/smoothness/images/*.*',
                'static/dailyreport/js/*.*',
                'static/dailyreport/jstree/*.*',
                'static/dailyreport/jstree/tree-themes/apple/*.*',
                'static/dailyreport/jstree/tree-themes/classic/*.*',
                'static/dailyreport/jstree/tree-themes/default/*.*',
                'static/dailyreport/jstree/tree-themes/default-rtl/*.*',
                'static/dailyreport/plupload/jquery.plupload.queue/*.*',
                'static/dailyreport/plupload/jquery.plupload.queue/css/*.*',
                'static/dailyreport/plupload/jquery.plupload.queue/img/*.*',
                'static/dailyreport/plupload/jquery.ui.plupload/*.*',
                'static/dailyreport/plupload/jquery.ui.plupload/css/*.*',
                'static/dailyreport/plupload/jquery.ui.plupload/img/*.*',
                'static/dailyreport/plupload/js/*.*',
                'static/dailyreport/plupload/js/i18n/*.*',
                'static/dailyreport/print_settings/*.*',
                'static/dailyreport/sorttable/*.*',
                'templates/dailyreport/zh-tw/*.html',
                'templatetags/*.py',
        ],
    },
    author='John',
    author_email='johnisacoolboy@gmail.com',
    url='https://bitbucket.org/johnisacoolboy/dailyreport',
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