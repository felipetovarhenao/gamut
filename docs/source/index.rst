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
      
      <table class="img-table">
         <tr>
            <td>
               <span>
                  • Let's imagine we want the computer to reconstruct this <b>portait of Bob Ross</b>, 
                  but only using bits and pieces of other images. 
                  We will call this portait the <b>target</b>, and the collection of other 
                  images the <b>corpus</b>.
               </span>
            </td>
            <td>
               <img src="_static/bob_ross_target.jpeg" class="example-img" alt="bob-ross">         
            </td>
         </tr>
         <tr>
            <td>
               • Now, let's imagine we tell the computer that the <b>corpus</b> will be all available <b>emojis</b>.
               The computer will then try to find <i>the best</i> subset of emojis, based on how similar they are in shape, 
               color, and other features to the <b>target</b>, and attempt to reconstruct the portrait of Bob Ross.
            </td>
            <td>
               <img src="_static/emoji_corpus.png" class="example-img" alt="emoji">
            </td>
         </tr>
         <tr>
            <td>
               • Thus, the computer might give us something like this — <b>a portrat of Bob Ross, made with several emoji</b>.
               <br/>
               <br/>
               Although this wasn't actually done by a computer, but manually assembled by LA-based artist 
               <a href="https://en.wikipedia.org/wiki/Yung_Jake" rel="noreferrer" target="_blank">Yung Jake</a> 
               with the <a href="http://android.emoji.ink" rel="noreferrer" target="_blank">emoji.ink</a> tool, 
               the idea still holds — <i>audio mosaicing</i> consists of reconstructing a <b>target</b> using a <b>corpus</b>, 
               but with audio instead of images. 
               <br/>
               <br/>
               The computer would then go through a collection of audio files, analyze every sound, and try to pick the bits and pieces (i.e., <i>audio grains</i>)
               that are most similar to the target, and assembled them into an <b>audio mosaic</b>.
            </td>
            <td>
               <img src="_static/bob_ross_yungjake.jpeg" class="example-img" alt="jung-jake">
            </td>
         </tr>
      </table>

Audio examples
~~~~~~~~~~~~~~~~

Here are 5 examples of `audio musaicing` made with **GAMuT**, using different **corpora** on the same audio **target**.

   .. raw:: html

      <table class='audio-examples-table'>
         <thead>
            <tr>
               <td>
                  <i><b>Target name</b></i>
               </td>
               <td>
               </td>
               <td>
                  <i><b>Audio input</b></i>
               </td>
            </tr>
         </thead>
         <tbody>
            <tr>
               <td>
                  An excerpt of Ángel Gonzalez' <i>muerte en el olvido</i>:
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
               </td>
               <td>
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/00+target_AG-muerte_en_el_olvido.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
            <tr class="corpus-example-header-row">
               <td>
                  <span>
                     <i><b>Corpus name</b></i>
                  </span>
               </td>
               <td>
                  <span>
                     <i><b>Corpus size</b></i>
                  </span>
               </td>
               <td>
                  <span>
                     <i><b>Audio output</b></i>
                  </span>
               </td>
            </tr>
            <tr>
               <td>
                  <b>Female singer voice corpus</b>
               </td>
               <td>
                  1221 audio files
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
            <tr>
               <td>
                  <b>Cmaj7 chord notes corpus</b>
               </td>
               <td>
                  340 audio files
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/02+CMaj_corpus+-+340+files.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
            <tr>
               <td>
                  <b>String instruments corpus</b>
               </td>
               <td>
                  1234 audio files
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/03+String_corpus+-+1234+files.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
            <tr>
               <td>
                  <b>Tam-tam corpus</b>
               </td>
               <td>
                  2878 audio files
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/04+Tamtam_corpus+-+2878+files.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
            <tr>
               <td>
                  <b>Woodwinds corpus</b>
               </td>
               <td>
                  412 audio files
               </td>
               <td>
                  <audio controls="controls">
                     <source src="https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/05+Wind_corpus+-+412+files.mp3" type="audio/wav">
                     Your browser does not support the <code>audio</code> element. 
                  </audio>
               </td>
            </tr>
         </tbody>
      </table>


.. toctree::
   :maxdepth: 3
   :caption: Table of contents:

   installation
   getting-started
   modules
   
To visualize contents in alphabetical order, see :ref:`genindex`.
