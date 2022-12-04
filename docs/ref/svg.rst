===============================
Scalable Vector Graphic Support
===============================

Scalable Vector Graphics (SVG) is an XML-based vector image format for two-dimensional graphics with support for
interactivity and animation. The SVG specification is an open standard developed by the World Wide Web Consortium (W3C).

Thumbnailing vector graphic images doesn't really make sense, because being in vector format they can scale to any size
without any quality of loss. However, users of **easy-thumbnails** may want to upload and use SVG images just as if
they would be in PNG, GIF or JPEG format. End users don't necessarily care about the format and definitely don't want
to convert them to a pixel based format. What they want is to reuse their templates with the templatetag
``{% thumbnail image ... as thumb %}``, and scale and crop the images to whatever the
element tag ``<img src="{{ thumb.url }}" width="..." height="...">`` has been prepared for.

This is done by adding an emulation layer named VIL, which aims to be compatible with PIL. All thumbnailing operations,
such as scaling and cropping behave like their pixel based counterparts. The content and final filesize of such
thumbnailed SVG images doesn't of course change, but their width/height and bounding box may be adjusted to reflect the
desired size of the thumbnailed image. Therefore, "thumbnailed" SVG images are stored side by side with their original
images and hence can be used by third-party apps such as
`django-filer<https://django-filer.readthedocs.io/en/latest/>`_ without modification.

Since easy-thumbnails version 2.8, you can therefore use an SVG image, just as you would use any other image.

This requires easy-thumbnails to have been installed with the ``[svg]`` extra enabled.

Cropping an SVG image works as expected. Filtering an SVG image will however not work.
