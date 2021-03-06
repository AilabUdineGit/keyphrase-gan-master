from nltk.stem.porter import *
stemmer = PorterStemmer()


def prediction_to_sentence(prediction, idx2word, vocab_size, oov, eos_idx, unk_idx=None, replace_unk=False, src_word_list=None, attn_dist=None):
    """
    :param prediction: a list of 0 dim tensor
    :param attn_dist: tensor with size [trg_len, src_len]
    :return: a list of words, does not include the final EOS
    """
    sentence = []
    for i, pred in enumerate(prediction):
        _pred = int(pred.item())  # convert zero dim tensor to int
        if i == len(prediction) - 1 and _pred == eos_idx:  # ignore the final EOS token
            break
        # replace_unk = False  # gl: old code
        if _pred < vocab_size:
            if _pred == unk_idx and replace_unk:
                assert src_word_list is not None and attn_dist is not None, "If you need to replace unk, you must supply src_word_list and attn_dist"
                # _, max_attn_idx = attn_dist[i].max(0)
                _, max_attn_idx = attn_dist[i].topk(2, dim=0)
                if max_attn_idx[0] < len(src_word_list):
                    word = src_word_list[int(max_attn_idx[0].item())]
                else:
                    word = src_word_list[int(max_attn_idx[1].item())]
                    # word = pykp.io.EOS_WORD
            else:
                word = idx2word[_pred]  # gl: resume of original code
                # print("The ",_pred," is")
                # word = idx2word[_pred]
                # word = _pred  # gl: old code
        else:
            # word = oov[pred - vocab_size]
            word = oov[_pred - vocab_size]  # gl: resume of original code
            # word = _pred - vocab_size  # gl: old code
        sentence.append(word)
    
    return sentence


def convert_list_to_kphs_old(keyphrases):
    total = []
    one_list = []
    print('keyphrases')
    print(keyphrases)
    for i, keyphrase in enumerate(keyphrases):
        # print(i)  # gl: debug
        # print(keyphrase)  # gl: debug
        # one_keyphrase = []
        # mapper = map(keyphrase,str)
        # mapper = ' '.join(mapper)
        # print(mapper)
        one_keyphrase = []
        for j, word_keyphrase in enumerate(keyphrase):
            # print(word_keyphrase)
            if int(word_keyphrase.item()) == 2:  # gl: <eos>
                if one_keyphrase != []:
                    one_list.append(one_keyphrase) 
                break                
            elif int(word_keyphrase.item()) != 4 and int(word_keyphrase.item()) != 5:  # gl: 4=<sep>; 5=<peos>
                # print("fdedh")
                one_keyphrase.append(int(word_keyphrase.item()))
            else:
                if one_keyphrase != []:
                    one_list.append(one_keyphrase) 
                one_keyphrase = []
        total.append(one_list)
        print('one_list')
        print(one_list)
        one_list = []
    # print(total[0])
    return total


def convert_list_to_kphs(keyphrases, eos_word, sep_word, peos_word, separate_present_absent=False):
    total = []
    one_list = []
    # print('keyphrases')  # gl: debug
    # print(keyphrases)  # gl: debug
    for i, keyphrase in enumerate(keyphrases):
        # print(i)  # gl: debug
        # print(keyphrase)  # gl: debug
        # one_keyphrase = []
        # mapper = map(keyphrase,str)
        # mapper = ' '.join(mapper)
        # print(mapper)
        one_keyphrase = []
        for j, word_keyphrase in enumerate(keyphrase):
            # print(word_keyphrase)
            # if int(word_keyphrase.item()) == 2:  # gl: old code
            if str(word_keyphrase.item()) == eos_word:
                if one_keyphrase != []:
                    one_list.append(one_keyphrase)
                break
            # elif int(word_keyphrase.item()) == 5:
            elif str(word_keyphrase.item()) == peos_word:
                if separate_present_absent:
                    if one_keyphrase != []:
                        one_list.append(one_keyphrase)
                    # one_list.append([int(word_keyphrase.item())])  # gl: old code
                    one_list.append([str(word_keyphrase.item())])
                    one_keyphrase = []
                else:
                    if one_keyphrase != []:
                        one_list.append(one_keyphrase)
                    one_keyphrase = []
            # elif int(word_keyphrase.item()) != 4:  # gl: old code
            elif str(word_keyphrase.item()) != sep_word:
                # print("fdedh")
                # one_keyphrase.append(int(word_keyphrase.item()))  # gl: old code
                one_keyphrase.append(str(word_keyphrase.item()))
            else:
                if one_keyphrase != []:
                    one_list.append(one_keyphrase)
                one_keyphrase = []
        total.append(one_list)
        # print('one_list')  # gl: debug
        # print(one_list)  # gl: debug
        one_list = []
    # print(total[0])
    return total


def stem_str_2d_list(str_2dlist):
    # stem every word in a list of word list
    # str_list is a list of word list
    stemmed_str_2dlist = []
    for str_list in str_2dlist:
        stemmed_str_list = [stem_word_list(word_list) for word_list in str_list]
        stemmed_str_2dlist.append(stemmed_str_list)
    return stemmed_str_2dlist


def stem_str_list(str_list):
    # stem every word in a list of word list
    # str_list is a list of word list
    stemmed_str_list = []
    for word_list in str_list:
        stemmed_word_list = stem_word_list(word_list)
        stemmed_str_list.append(stemmed_word_list)
    return stemmed_str_list


def stem_word_list(word_list):
    return [stemmer.stem(w.strip().lower()) for w in word_list]


"""
def split_concated_keyphrases(word_list, delimiter_word):
    tmp_pred_str_list = []
    tmp_word_list = []
    for word in word_list:
        if word != delimiter_word:
            tmp_word_list.append(word)
        else:
            if len(tmp_word_list) > 0:
                tmp_pred_str_list.append(tmp_word_list)
                tmp_word_list = []
    if len(tmp_word_list) > 0:  # append the final keyphrase to the pred_str_list
        tmp_pred_str_list.append(tmp_word_list)
    return tmp_pred_str_list
"""


def split_word_list_by_delimiter(word_list, keyphrase_delimiter, include_present_absent_delimiter=False, present_absent_delimiter=None):
    """
    Convert a word list into a list of keyphrase, each keyphrase is a word list.
    :param word_list: word list of concated keyprhases, separated by a delimiter
    :param keyphrase_delimiter
    :param include_present_absent_delimiter: if it is true, the final list of keyphrase will include the present_absent_delimiter as one of the keyphrase, e.g., [['kp11', 'kp12'], ['<peos>'], ['kp21', 'kp22']]
    :param present_absent_delimiter
    :return: a list of keyphrase, each keyphrase is a word list.
    """
    if include_present_absent_delimiter:
        assert present_absent_delimiter is not None
    tmp_pred_str_list = []
    tmp_word_list = []
    # print(word_list)  # gl: debug
    for word in word_list:
        # print("The asf IS",keyphrase_delimiter)
        # keyphrase_delimiter = 4  # gl: non necessario
        if word == keyphrase_delimiter:
            if len(tmp_word_list) > 0:
                tmp_pred_str_list.append(tmp_word_list)
                tmp_word_list = []
        # elif word == present_absent_delimiter and include_present_absent_delimiter:  # gl: se w=<peos> ma include_present_absent_delimiter=False, aggiunge <peos> alla lista,non va bene
        #     if len(tmp_word_list) > 0:
        #         tmp_pred_str_list.append(tmp_word_list)
        #         tmp_word_list = []
        #     tmp_pred_str_list.append([present_absent_delimiter])
        elif word == present_absent_delimiter:  # gl: così gestisce <peos> solo nel caso separated, mentre lo tralascia nel caso sorted
            # print('<peos> found in generated sample!')  # gl: debug
            if include_present_absent_delimiter:
                if len(tmp_word_list) > 0:
                    tmp_pred_str_list.append(tmp_word_list)
                    tmp_word_list = []
                tmp_pred_str_list.append([present_absent_delimiter])
            else:  # gl: 13 august 2020
                if len(tmp_word_list) > 0:
                    tmp_pred_str_list.append(tmp_word_list)
                    tmp_word_list = []
        else:
            tmp_word_list.append(word)

    if len(tmp_word_list) > 0:  # append the final keyphrase to the pred_str_list
        tmp_pred_str_list.append(tmp_word_list)
    # print(tmp_pred_str_list)  # gl: debug
    return tmp_pred_str_list
