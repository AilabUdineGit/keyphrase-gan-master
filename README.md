# Keyphrase GAN with Bert Discriminator
We are implementing a GAN architecture to generate high-quality Keyphrases (KPs) from scientific abstracts. Our work starts from <a href="https://github.com/avinsit123/keyphrase-gan">Keyphrase-GAN</a> wich, in turn, uses the Generator from <a href = "https://github.com/kenchan0226/keyphrase-generation-rl"> keyphrase-generation-rl </a> and <a href = "https://github.com/memray/seq2seq-keyphrase-pytorch"> seq2seq-keyphrase-pytorch </a> .
We introduce a novel Bert Discriminator.

Output of Discriminator is used to evaluate rewards for the Reinforcement Learning (RL) of the Generator.

## Dataset and Data Preprocessing
Kp20k dataset is used to train both Generator (G) and Discriminator (D). Dataset is composed by +500k sample documents, each consisting of a scientific abstracts and the related KPs.
To preprocess the data run: 
```terminal
python3 preprocess.py -data_dir data/kp20k_separated -remove_eos -include_peos -sample_size 2000
```
Specify `-sample_size` option to put an upper limit; default value is `1000`.

## Bert model for Discriminator
Different Bert models from <a href = https://github.com/huggingface/transformers> Huggingface Transformers </a> have been tested.
Currently used model is <a href = https://huggingface.co/transformers/model_doc/bert.html#bertforsequenceclassification> BertForSequenceClassification </a>. It can be used to perform both classification passing it an `option.num_labels >= 2`, or regression with `option.num_labels = 1`. Current model in use is a regressor so `option.num_labels = 1`; in this case classification is performed by splitting the output in two classes: `> 0.5` (real sample) and `< 0.5` (fake sample).

Some changes have been made in the structure, notably the output to classify the sample is not retrieved from the [CLS] token but from an average of _all_ the input tokens (cfr. <a href = https://huggingface.co/transformers/model_doc/bert.html#bertmodel> BertModel </a>: `pooler_output` in the `Returns` section) 

### Bert input
The Discriminator performs the task of splitting the real KPs (generated by humans) from the fake ones (generated by the last version of Generator), for each sample document.
In order to be used as Bert input, samples has to be Bert-tokenized. <a href = https://github.com/google-research/bert#tokenization > Here </a> more details about Bert tokenization.
The final pattern is:
```terminal
[CLS] <abstract> [SEP] <KP1> ; <KP2> ; ... ; <KPn> [SEP]
```
where `[CLS]` is the special starting token, `[SEP]` is the special separation and ending token, `<abstract>` are the tokens of the abstract, `<KPi>` are those of the _i-th_ KP, and `;` separates different KPs.
Total length of input sequence is cut to `bert_max_length = 320` or `bert_max_length = 384`

### Training of Discriminator
During D training, for each abstract two input sequences as above are built: one with the real KPs, and one with the fake ones. Then the model is trained with both real and fake sequences, each with the appropriate label: 0 for fake, 1 for real.

Be sure the option `-use_bert_discriminator` in config.py is set to True, then run
```terminal
python3 GAN_Training.py  -data data/kp20k_separated/ -vocab data/kp20k_separated/ -exp_path exp/%s.%s -exp kp20k -epochs 5 -copy_attention -train_ml -one2many -one2many_mode 1 -batch_size 4 -model [MLE_model_path] -train_discriminator 
```
As Bert models are highly memory consuming, `batch_size` depends much on the length of the input sequence: for `bert_max_length = 320` you will have `batch_size = 4`, for `bert_max_length = 384` you will have `batch_size = 3`.

### Bert output
A tuple of tensors is returned as output:
- output[0]: classification or regression loss, float tensor of shape `(1,)`, only returned if _labels_ are provided in input;
- output[1]: classification or regression scores, float tensor of shape `(batch_size, config.num_labels)`;
- output[2]: hidden states, tuple of float tensors (one for each layer) of shape `(batch_size, sequence_length, hidden_size)`.

Currently used values are: `config.num_labels = 1` (regression), `batch_size = 4`, `sequence_length = 320`, `hidden_size = 768`.

## Generator
For Generator we use CatSeq, an encoder-decoder model.
To train the Generator run
```terminal
python3 GAN_Training.py  -data data/kp20k_separated/ -vocab data/kp20k_separated/ -exp_path exp/%s.%s -exp kp20k -epochs 20 -copy_attention -train_ml -one2many -one2many_mode 1 -batch_size 32 -model [model path] -train_rl -replace_unk -Discriminator_model_path [discriminator path] 
```


