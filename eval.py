import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from torch.optim import SGD
from datetime import datetime

from transformers import BertTokenizerFast
from transformers import BertForTokenClassification

df = pd.read_csv("ner.csv")

labels = [i.split() for i in df['labels'].values.tolist()]
unique_labels = set()
for lb in labels:
    [unique_labels.add(i) for i in lb if i not in unique_labels]

print(unique_labels)

labels_to_ids = {k: v for v, k in enumerate(sorted(unique_labels))}
ids_to_labels = {v: k for v, k in enumerate(sorted(unique_labels))}
print(labels_to_ids)


label_all_tokens = True

def align_label(texts, labels):
    tokenized_inputs = tokenizer(texts, padding='max_length', max_length=512, truncation=True)

    word_ids = tokenized_inputs.word_ids()

    previous_word_idx = None
    label_ids = []

    for word_idx in word_ids:

        if word_idx is None:
            label_ids.append(-100)

        elif word_idx != previous_word_idx:
            try:
                label_ids.append(labels_to_ids[labels[word_idx]])
            except:
                label_ids.append(-100)
        else:
            try:
                label_ids.append(labels_to_ids[labels[word_idx]] if label_all_tokens else -100)
            except:
                label_ids.append(-100)
        previous_word_idx = word_idx

    return label_ids

class DataSequence(torch.utils.data.Dataset):

    def __init__(self, df):

        lb = [i.split() for i in df['labels'].values.tolist()]
        txt = df['text'].values.tolist()
        self.texts = [tokenizer(str(i),
                               padding='max_length', max_length = 512, truncation=True, return_tensors="pt") for i in txt]
        self.labels = [align_label(i,j) for i,j in zip(txt, lb)]

    def __len__(self):

        return len(self.labels)

    def get_batch_data(self, idx):

        return self.texts[idx]

    def get_batch_labels(self, idx):

        return torch.LongTensor(self.labels[idx])

    def __getitem__(self, idx):

        batch_data = self.get_batch_data(idx)
        batch_labels = self.get_batch_labels(idx)
        return batch_data, batch_labels

# We split the data into train, validation and test sets (80-10-10 split)
df_train, df_val, df_test = np.split(df.sample(frac=1, random_state=42),
                            [int(.8 * len(df)), int(.9 * len(df))])

tokenizer = BertTokenizerFast.from_pretrained('bert-base-cased')
# Note how we are using the cased version of tokenizer here since the labels leverage the case information


class BertModel(torch.nn.Module):

    def __init__(self):
        super(BertModel, self).__init__()
        self.bert = BertForTokenClassification.from_pretrained('bert-base-cased', num_labels=len(unique_labels))

    def forward(self, input_id, mask, label):
        output = self.bert(input_ids=input_id, attention_mask=mask, labels=label, return_dict=False)
        return output
    
    
model = torch.load("BERT_epoch_5_17-04-2023-10:26.pt")


# def evaluate(model, df_test):

#     test_dataset = DataSequence(df_test)

#     test_dataloader = DataLoader(test_dataset, num_workers=4, batch_size=1)

#     use_cuda = torch.cuda.is_available()
#     device = torch.device("cuda:1" if use_cuda else "cpu")
#     torch.cuda.set_device(device)
#     if use_cuda:
#         model = model.cuda()

#     total_acc_test = 0.0
#     total_alt_acc = float(0)
#     rem_count = 0
#     per_tok_acc = [0.0]*17
#     per_tok_rem = [0]*17
#     for ttt,data in enumerate(tqdm(test_dataloader)):
#             test_data, test_label = data[0], data[1]
#             test_label = test_label.to(device)
#             mask = test_data['attention_mask'].squeeze(1).to(device)

#             input_id = test_data['input_ids'].squeeze(1).to(device)

#             loss, logits = model(input_id, mask, test_label)
            
#             for i in range(logits.shape[0]):

#               logits_clean = logits[i][test_label[i] != -100]
#               label_clean = test_label[i][test_label[i] != -100]
#               non_o_ids = (torch.tensor(np.where(label_clean.detach().cpu().numpy() != 16 ))).to(device)
#               # if (True):
#               #   print(label_clean)
#               #   print(non_o_ids)
#               predictions = logits_clean.argmax(dim=1)
#               acc = (predictions == label_clean).float().mean()
#               total_acc_test += acc
#               for i in range(0,17):
#                 cur_labels = (torch.tensor(np.where(label_clean.detach().cpu().numpy() == i ))).to(device)
#                 temp_clean = label_clean[cur_labels]
#                 temp_predictions = predictions[cur_labels]
#                 acc_alt = (temp_predictions == temp_clean).float().sum()
#                 if (not torch.isnan(acc_alt).all()):
#                     per_tok_rem[i] += len(cur_labels[0])
#                     per_tok_acc[i] += acc_alt
#                     # print(float(acc_alt),len(cur_labels[0]))
#               label_clean = label_clean[non_o_ids]
#               predictions = predictions[non_o_ids]
#               #print(predictions == label_clean)
#               acc_alt = (predictions == label_clean).float().sum()
#               if (not torch.isnan(acc_alt).all()):
#                 rem_count += len(non_o_ids[0])
#                 total_alt_acc += float(acc_alt)
#                 #print(float(acc_alt),len(non_o_ids[0]))
                

                
#     for i in range(0,17):
#         print(f'Test Accuracy : {per_tok_acc[i]/ (per_tok_rem[i]): .3f} | {per_tok_rem[i]}' + " for label " + str(ids_to_labels[i]))
#     print(f'Test Accuracy: {total_acc_test / len(df_test): .3f}')
#     print(f'ALT Test Accuracy: {total_alt_acc / (rem_count): .3f}')



# evaluate(model, df_test)


def align_word_ids(texts):
  
    tokenized_inputs = tokenizer(texts, padding='max_length', max_length=512, truncation=True)

    word_ids = tokenized_inputs.word_ids()

    previous_word_idx = None
    label_ids = []

    for word_idx in word_ids:

        if word_idx is None:
            label_ids.append(-100)

        elif word_idx != previous_word_idx:
            try:
                label_ids.append(1)
            except:
                label_ids.append(-100)
        else:
            try:
                label_ids.append(1 if label_all_tokens else -100)
            except:
                label_ids.append(-100)
        previous_word_idx = word_idx

    return label_ids


def evaluate_one_text(model, sentence):


    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    if use_cuda:
        model = model.cuda()

    text = tokenizer(sentence, padding='max_length', max_length = 512, truncation=True, return_tensors="pt")

    mask = text['attention_mask'].to(device)
    input_id = text['input_ids'].to(device)
    label_ids = torch.Tensor(align_word_ids(sentence)).unsqueeze(0).to(device)

    logits = model(input_id, mask, None)
    logits_clean = logits[0][label_ids != -100]

    predictions = logits_clean.argmax(dim=1).tolist()
    prediction_label = [ids_to_labels[i] for i in predictions]
    print(sentence)
    print(prediction_label)
            
evaluate_one_text(model, 'During Republic day of India an earthquake occured while the president hoist the flag at the Red Fort')