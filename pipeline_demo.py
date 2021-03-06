import sys
import argparse
import io
import json
import stanfordnlp

if __name__ == '__main__':
    """
        input:
            - model_dir
            - model
        TODO: 
        - txt based input : because limit of child-process argmax size is 131KB.
            - x-www- => form-data 
            - or separate path
            - use uuid for store txt data
        - separate returned json value
            - check needed parameter
            => parameter serialization
        - use GPU for fasting speed
    """
    # get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--models_dir', help='location of models files | default: ./models/', default='./models')
    parser.add_argument('-m', '--model', help='lang_treebank', default="ko")
    parser.add_argument('-p', '--path', default=None)
    parser.add_argument('-i', '--input', help='sentences', default=None)
    args = parser.parse_args()

    input_txt = True

    lang, treebank = args.model.split('_')
    
    if args.path == None :
        input_txt = False
    
    if args.input == None and input_txt is False :
        sys.exit(1)

    if input_txt is True:
        txt_path = args.path

        file = open(txt_path, 'r')
        input = file.read()
        file.close()
        input = ' '.join(input.split('\n'))
        sentences = { lang : input }
        
    if  input_txt is False :
        sentences = { lang : args.input }

    if len(sentences[lang]) == 0 :
        print(json.dumps({}, ensure_ascii=False))
        sys.exit(1)
    
    text_trap = io.StringIO()
    sys.stdout = text_trap
    sys.stderr = text_trap
    
    conll = args.model
    # set up a pipeline
    pipeline = stanfordnlp.Pipeline(models_dir=args.models_dir, lang=lang, treebank=conll, use_gpu=False)
    
    # process the document
    doc = pipeline(sentences[lang])

    obj = { }
    
    for scnt, sentence in enumerate(doc.sentences):
        obj[scnt] = []
        for wcnt, word in enumerate(sentence.words):
            temp = {
                'index' : int(word.index),
                'word' : word.text,
                'lemma' : word.lemma,
                'upos' : word.upos,
                'xpos' : word.xpos,
                'feats' : word.feats,
                'governor_index' : word.governor,
                'governor' : (sentence.words[word.governor-1].text if word.governor > 0 else 'root'),
                'dependecy_relation' : word.dependency_relation,
                #'parent_token' : word.parent_token,
            }
            obj[scnt].append(temp)

    sys.stdout = sys.__stdout__        
    print(json.dumps(obj, ensure_ascii=False))