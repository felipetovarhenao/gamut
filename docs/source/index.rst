.. GAMuT documentation master file, created by
   sphinx-quickstart on Sun Jan 29 15:08:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GAMuT documentation
=================================

.. image:: _static/gamut-logo.png
   :align: center
   :height: 200px

Description
---------------------------------

**GAMuT** is a high-level, user-friendly granular audio musaicing toolkit implemented in Python. 
Here are 5 examples of `audio musaicing` , using different corpora on the same target:

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
                  An excerpt of Ángel Gonzalez' <i>muerte en el olvido</i>.
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
