import pandas as pd
import requests
import json
from random import randrange, choice
import datetime 
import pprint

database_Sim = "Attention Is All You Need Ashish Vaswani∗ Google Brain avaswani@google.com Noam Shazeer∗ Google Brain noam@google.com Niki Parmar∗ Google Research nikip@google.com Jakob Uszkoreit∗ Google Research usz@google.com Llion Jones∗ Google Research llion@google.com Aidan N. Gomez∗† University of Toronto aidan@cs.toronto.edu Łukasz Kaiser∗ Google Brain lukaszkaiser@google.com Illia Polosukhin∗ illia.polosukhin@gmail.com Abstract The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder conﬁguration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring signiﬁcantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English- to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.0 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data. 1 Introduction Recurrent neural networks, long short-term memory [12] and gated recurrent [7] neural networks in particular, have been ﬁrmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation [31, 2, 5]. Numerous efforts have since continued to push the boundaries of recurrent language models and encoder-decoder architectures [34, 22, 14]. Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states ht, as a function of the previous hidden state ht−1 and the input for position t. This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples. Recent work has achieved signiﬁcant improvements in computational efﬁciency through factorization tricks [19] and conditional ∗Equal contribution. Listing order is random. †Work performed while at Google Brain. arXiv:1706.03762v1 [cs.CL] 12 Jun 2017 computation [29], while also improving model performance in case of the latter. The fundamental constraint of sequential computation, however, remains. Attention mechanisms have become an integral part of compelling sequence modeling and transduc- tion models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences [2, 17]. In all but a few cases [25], however, such attention mechanisms are used in conjunction with a recurrent network. In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for signiﬁcantly more parallelization and can reach a new state of the art in translation quality after being trained"

userprompt = """
what is attention is all you need about ?
"""

promptrule = """
Summaries the given input for the given question.
"""


finalprompt = f'''
{database_Sim}
with the information above Summaries the answer for the following question:

{userprompt}
{promptrule}

'''


url = "http://localhost:11434/api/chat"
data = {
    "model": "mistral:7b-instruct-q4_K_M",
    "temperature": 0.2,
    "messages": [
        {"role": "user", "content": finalprompt,},
    ],
    "stream": False
}



print("User: ", finalprompt)
response = requests.post(url, json=data)
content = res = json.loads(response.text)



print("CyLLM:")
print(content["message"]["content"].replace("<|eot_id|>", ""))


print("-"*60)