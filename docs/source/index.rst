GAMuT documentation
=================================

.. image:: _static/gamut-logo.png
   :align: center
   :height: 200px

Description
---------------------------------

**GAMuT** is a high-level, user-friendly granular `audio musaicing` toolkit implemented in Python. `Audio musaicing` (also spelled `mosaicing`), 
can be `defined <http://imtr.ircam.fr/imtr/Audio_Mosaicing>`_ as **"the process of recomposing the temporal evolution of a given target audio file from segments cut out of source audio materials"**.

Audio musaicing: A visual analogy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're new to `audio musaicing`, let's consider the following visual analogy:

   .. raw:: html
      
      <div class="img-grid">
         <div>
            <span>
               • Let's imagine we want the computer to reconstruct this <b>portait of Bob Ross</b>, 
               but only using bits and pieces of other images. 
               We will call this portait the <b>target</b>, and the collection of other 
               images the <b>corpus</b>.
            </span>
         </div>
         <div>
            <img src="_static/bob_ross_target.jpeg" class="example-img" alt="bob-ross">    
            <span class="caption">The target: A portrait of Bob Ross</span>     
         </div>
         <div>
            • Now, let's imagine we tell the computer that the <b>corpus</b> will be all available <b>emojis</b>.
            The computer will then try to find <i>the best</i> subset of emojis, based on how similar they are in shape, 
            color, and other features to the <b>target</b>, and attempt to reconstruct the portrait of Bob Ross.
         </div>
         <div>
            <img src="_static/emoji.webp" class="example-img" alt="emoji">
            <span class="caption">The corpus: A collection of emoji</span>     
         </div>
         <div>
            • Thus, the computer might give us something like this — <b>a portrat of Bob Ross, made with several emoji</b>.
            <br/>
            <br/>
            Although this wasn't actually done by a computer, but manually drawn by LA-based artist 
            <a href="https://en.wikipedia.org/wiki/Yung_Jake" rel="noreferrer" target="_blank">Yung Jake</a> 
            with the <a href="http://android.emoji.ink" rel="noreferrer" target="_blank">emoji.ink</a> tool, 
            the idea still holds — <i>audio mosaicing</i> consists of reconstructing a <b>target</b> using a <b>corpus</b>, 
            but with audio instead of images. 
            <br/>
            <br/>
            The computer would then go through a collection of audio files, analyze every sound, and try to pick the bits and pieces (i.e., <i>audio grains</i>)
            that are most similar to the target, and assembled them into an <b>audio mosaic</b>.
         </div>
         <div>
            <img src="_static/bob_ross_yungjake.jpeg" class="example-img" alt="jung-jake">
            <span class="caption">Visual analogy of audio musaicing: Emoji Bob Ross (by Yung Jake)</span>    
         </div>
      </div>

Audio examples
~~~~~~~~~~~~~~~~

Here are **3 examples** of `audio musaicing` made with **GAMuT**, each using different **corpora** on the same audio **target**.

**Example 1**

   .. raw:: html

      <div class='audio-examples-grid'>
         <div>
            <i><b>Target name</b></i>
         </div>
         <div></div>
         <div>
            <i><b>Audio input</b></i>
         </div>
         <div>
            Excerpt of Ángel Gonzalez'&nbsp;<i>muerte en el olvido</i>:
            <br/>
            <br/>
            <div class="poem">
               <i>Yo sé que existo</i>
               <br/>
               <i>porque tú me imaginas.</i>
               <br/>
               <i>Soy alto porque tú me crees</i>
               <br/>
               <i>alto, y limpio porque tú me miras</i>
               <br/>
               <i>con buenos ojos,</i>
               <br/>
               <i>con mirada limpia.</i>
               <br/>
            </div>
         </div>
         <div>
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/00+target_AG-muerte_en_el_olvido.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <span>
               <i><b>Corpus name</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Corpus size</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Audio output</b></i>
            </span>
         </div>
         <div>
            <b>Female singer voice corpus</b>
         </div>
         <div>
            1221 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Cmaj7 chord notes corpus</b>
         </div>
         <div>
            340 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/02+CMaj_corpus+-+340+files.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>String instruments corpus</b>
         </div>
         <div>
            1234 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/03+String_corpus+-+1234+files.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Tam-tam corpus</b>
         </div>
         <div>
            2878 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/04+Tamtam_corpus+-+2878+files.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Woodwinds corpus</b>
         </div>
         <div>
            412 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/05+Wind_corpus+-+412+files.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
      </div>

**Example 2**

   .. raw:: html

      <div class='audio-examples-grid'>
         <div>
            <i><b>Target name</b></i>
         </div>
         <div></div>
         <div>
            <i><b>Audio input</b></i>
         </div>
         <div>
            Drumset loop
         </div>
         <div>
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/drums.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <span>
               <i><b>Corpus name</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Corpus size</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Audio output</b></i>
            </span>
         </div>
         <div>
            <b>Electric guitar corpus</b>
         </div>
         <div>
            28 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/electric-guitar-drums.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Animal sounds corpus</b>
         </div>
         <div>
            51 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/animal-drums.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Vocal sounds corpus</b>
         </div>
         <div>
            768 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/vocal-drums.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
      </div>

**Example 3**

   .. raw:: html

      <div class='audio-examples-grid'>
         <div>
            <i><b>Target name</b></i>
         </div>
         <div></div>
         <div>
            <i><b>Audio input</b></i>
         </div>
         <div>
            Excerpt from J.S. Bach's&nbsp;<i>Badinerie</i>
         </div>
         <div>
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/badinerie.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <span>
               <i><b>Corpus name</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Corpus size</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Audio output</b></i>
            </span>
         </div>
         <div>
            <b>Orchestral music corpus</b>
         </div>
         <div>
            64 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/orchestral-badinerie.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Percussion corpus</b>
         </div>
         <div>
            282 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/percussion-badinerie.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Violin sounds corpus</b>
         </div>
         <div>
            658 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/violin-badinerie.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
      </div>
   
**Example 4**

   .. raw:: html

      <div class='audio-examples-grid'>
         <div>
            <i><b>Target name</b></i>
         </div>
         <div></div>
         <div>
            <i><b>Audio input</b></i>
         </div>
         <div>
            Female pop singer
         </div>
         <div>
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/singer.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <span>
               <i><b>Corpus name</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Corpus size</b></i>
            </span>
         </div>
         <div>
            <span>
               <i><b>Audio output</b></i>
            </span>
         </div>
         <div>
            <b>Piano corpus</b>
         </div>
         <div>
            177 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/piano-singer.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Violin corpus</b>
         </div>
         <div>
            658 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/violin-singer.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
         <div>
            <b>Commercial music corpus</b>
         </div>
         <div>
            140 audio files
         </div>
         <div>
            <audio controls="controls">
               <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/pop-singer.mp3" type="audio/mpeg">
               Your browser does not support the <code>audio</code> element. 
            </audio>
         </div>
      </div>

.. toctree::
   :maxdepth: 3
   :caption: Table of contents:

   installation
   getting-started
   command-line-interface
   modules
   
To visualize contents in alphabetical order, see :ref:`genindex`.
