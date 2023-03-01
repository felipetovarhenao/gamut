Graphical user interface
=========================

Setup
~~~~~~~~~~~

Once **GAMuT** has been :doc:`installed <../installation>`, we need to ensure the `kivy <https://kivy.org/>`_ library is also installed, by running:

    .. code:: shell
        
        pip install "kivi[base]"

If this goes well, we can use **GAMuT**'s graphical user interface (GUI).


Running the application
~~~~~~~~~~~~~~~~~~~~~~~~

To launch the **GAMuT** GUI, simply run:

    .. code:: shell

        gamut --gui

Being the first time to run the application, it might take longer to load than it's supposed to. If everything goes well, the application should open up.
Although hopefully the interface is self-explanatory enough to not require explanation, you can read more about each of the different modules and paremeters here:

    * :class:`corpus<gamut.features.Corpus>`
    * :class:`mosaic<gamut.features.Mosaic>`
    * :class:`audio<gamut.features.Mosaic.to_audio>`
        

