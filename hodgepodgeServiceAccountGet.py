#!/usr/bin/python
##
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##
#
# Copyright 2014 UnicornDelight <unicorn@mapledash.com>
#
#     Referencing the samples Google supplied, I made an (not complete)
#     "all-in-one" script to get various Google Play listing data. Added
#     other resources that Google had no examples for. Tested with a
#     medium volume of data (about 40 listings) with no issues.
#
#     The main reason for making this was for the looping factor. You can
#     loop the process over easy by specifying all the package names you
#     want information for. I plan on adding file import support for the
#     package names as well as various other import options such as MySQL.
#
#     In addition, I have added the ability to select any resource you would
#     like to get details for. I plan on adding more later. Will be adding
#     additional things such as output to MySQL, JSON, CSV, along with the
#     ability to select whether to upload or download data.
#
#     Thanks goes to Google (Copyright 2014 Google Inc. All Rights Reserved)
#     for supplying the quick small samples that allowed me to write this
#     up in a few hours. Google Examples: http://goo.gl/eBLCqA
#
##

##
# Usage Argument Examples:
#     --packages com.unicorndelight.magic
#     -l en-US
#     --resources listings details apks images
#     --imagetypes icon featureGraphic phoneScreenshots promoGraphic
#
# Full API docs at: https://developers.google.com/android-publisher/
##

"""A hodgepodge of info for a given application based on the package name."""

import argparse
from apiclient.discovery import build
import httplib2
from oauth2client import client

SERVICE_ACCOUNT_EMAIL = (
    'ENTER_YOUR_SERVICE_ACCOUNT_EMAIL_HERE@developer.gserviceaccount.com')

def edit_request(service, package):
    """Request the edit id using the package name"""
    request = service.edits().insert(body={}, packageName=package)
    result = request.execute()
    return result['id']

def listings_get(service, edit_id, package, lang):
    """Retrieve data from the listings resource"""
    listings = service.edits().listings().get(
        editId=edit_id,
        language=lang,
        packageName=package).execute()

    if listings['title']:
        print '\t\tTitle: \"%s\"' % (
            listings['title'])
    if listings['shortDescription']:
        print '\t\tShortDescription: \"%s\"' % (
            listings['shortDescription'])
    if listings['fullDescription']:
        print '\t\tFullDescription: \"%s\"' % (
            listings['fullDescription'])
    if listings['video']:
        print '\t\tVideo: \"%s\"\n' % (
            listings['video'])

def details_get(service, edit_id, package):
    """Retrieve data from the details resource"""
    details = service.edits().details().get(
        editId=edit_id,
        packageName=package).execute()

    if details['contactEmail']:
        print '\t\tDetailsEmail: \"%s\"' % (
            details['contactEmail'])
    if details['contactPhone']:
        print '\t\tDetailsPhone: \"%s\"' % (
            details['contactPhone'])
    if details['contactWebsite']:
        print '\t\tDetailsWebsite: \"%s\"' % (
            details['contactWebsite'])
    if details['defaultLanguage']:
        print '\t\tDetailsLanguage: \"%s\"' % (
            details['defaultLanguage'])

def apks_list(service, edit_id, package):
    """Retrieve data from the apks resource"""
    apks_result = service.edits().apks().list(
        editId=edit_id,
        packageName=package).execute()

    for apk in apks_result['apks']:
        print '\t\tVersionCode: \"%s\" \n\t\tSHA1: \"%s\"' % (
             apk['versionCode'], apk['binary']['sha1'])

def images_list(images, imagetype):
    """Retrieve data from the images resource"""
    #Check to make sure that there is data for
    #the specified imagetype. If there is, then
    #print all of the data that is there
    if images:
        if images['images']:
            print '\t\t%s: ' % (imagetype)
            for image in images['images']:
                if image['id']:
                    print '\t\t\tID: \"%s\"' % (image['id'])
                if image['url']:
                    print '\t\t\tURL: \"%s\"' % (image['url'])
                if image['sha1']:
                    print '\t\t\tSHA1: \"%s\"' % (image['sha1'])
        else:
            print '\t\t%s: \"NOT_AVAILABLE\"' % (imagetype)

def process_imgtypes(service, edit_id, package, lang, imagetypes):
    """Run through the list of user supplied imagetype data to get"""
    for imagetype in imagetypes:
        images = service.edits().images().list(
            editId=edit_id,
            imageType=imagetype,
            language=lang,
            packageName=package).execute()

        return images_list(images, imagetype)

def hodgepodge(packages, lang, resources, imagetypes):
    """The main function that gets the data by running various functions"""

    # Load the key in PKCS 12 format that you downloaded from the Google APIs
    # Console when you created your Service account.
    keyfile = open('key.p12', 'rb')
    key = keyfile.read()
    keyfile.close()

    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with the Credentials. Note that the first parameter,
    # service_account_name, is the Email address created for the Service
    # account. It must be the email address associated with the key that
    # was created.
    credentials = client.SignedJwtAssertionCredentials(
        SERVICE_ACCOUNT_EMAIL,
        key,
        scope='https://www.googleapis.com/auth/androidpublisher')
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('androidpublisher', 'v2', http=http)

    for package in packages:
        try:
            #Request the edit id of the current package
            edit_id = edit_request(service, package)

            print 'EditID: \"%s\"' % (edit_id)
            print '\tPackage: \"%s\"' % (package)

            #listings, details, apks, and images resource
            if 'listings' in resources:
                print '\tListings: '
                listings_get(service, edit_id, package, lang)

            if 'details' in resources:
                print '\tDetails: '
                details_get(service, edit_id, package)

            if 'apks' in resources:
                print '\tAPKs: '
                apks_list(service, edit_id, package)

            if 'images' in resources:
                print '\tImages: '
                process_imgtypes(service, edit_id, package, lang, imagetypes)

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please'
                're-run the application to re-authorize')

    #Everything is now complete so why not say a friendly goodbye?
    print 'Complete! Have a magical day, you delightful thing!'

def main():
    """Start the hodgepodge if all checks pass."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--packages', nargs='*', required=True,
        help='The package name. Example: com.unicorndelight.magic')
    parser.add_argument('-l', '--language', default='en-US',
        help='Set the language to be used. Example: en-US')
    parser.add_argument('-r', '--resources', nargs='*', default=None,
        help='The various resources to be requested. Example: listings')
    parser.add_argument('-i', '--imagetypes', nargs='*', default=None,
        help='The types of images to be requested; Example: icon')
    args = parser.parse_args()

    #A few initial checks and error messages before running
    if args.resources is None:
        print 'Oops! You must supply at least one type of resource.'

    else:
        if 'images' in args.resources:
            if args.imagetypes is None:
                print ('Oops! You must supply at least one imagetype '
                    'required for the "Images" resource')

        hodgepodge(
            args.packages,
            args.language,
            args.resources,
            args.imagetypes)

if __name__ == '__main__':
    main()
