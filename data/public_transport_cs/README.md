Czech Public Transport – Data
=============================

The data in this directory are mostly converted from the [Alex](https://github.com/UFAL-DSG/alex) dialogue system.

Files' purpose:

* [cities.expanded.txt](./cities.expanded.txt), [cities.expanded.txt](./stops.expanded.txt), [cities.expanded.txt](./train_names.expanded.txt) – list of inflected city, stop, and train names loaded in the [database](../../dialmonkey/nlu/public_transport_cs/database.py) on NLU startup.
* [utt2da.tsv](./utt2da.tsv) – override direct utterance to DA mapping, loaded on NLU startup (based on the corresponding [configuration](../../conf/public_transport_cs.yaml) setting).
* [nlu_test_data.json](./nlu_test_data.json) – development/test data for NLU – the JSON structure is a list of examples, each with thi following entries:
  * "audio_file" – ID of the original audio recording. For some sentences, it starts with "bootstrap". These are hand-written, not recorded in a real system.
  * "usr" – user input, hand-written or transcribed from audio
  * "asr_out" – ASR output, can be very noisy and isn't recommended for use in the NLU (not present in hand-written instances)
  * "DA" – current NLU results, to be used for evaluation
  * "DA.old" – annotated with old Alex annotation results

Note that most files are versioned using [Git LFS](https://git-lfs.github.com/). 
If you didn't have Git LFS installed, remove the files in this directory, install Git LFS and checkout the files again.
