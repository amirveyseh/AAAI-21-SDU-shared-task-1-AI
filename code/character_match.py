import argparse
import json

def predict(data):
    predictions = []
    for d in data:
        pred = {
            'id': d['id'],
            'predictions': ['O']*len(d['tokens'])
        }
        for i, t in enumerate(d['tokens']):
            if t[0].isupper() and len([c for c in t if c.isupper()])/len(t) > 0.6 and 2 <= len(t) <= 10:
                pred['predictions'][i] = 'B-short'
                long_cand_length = min([len(t)+5,len(t)*2])
                cand_long = []
                cand_long_index = []
                left = True
                if i < len(d['tokens']) - 3 and d['tokens'][i+1] == '(':
                    left = False
                    for j in range(i+2,min([i+2+long_cand_length,len(d['tokens'])])):
                        if d['tokens'][j] != ')':
                            cand_long.append(d['tokens'][j])
                            cand_long_index.append(j)
                        else:
                            break
                elif 1 < i < len(d['tokens'])-3 and d['tokens'][i-1] == '(' and d['tokens'][i+1] == ')':
                    for k in range(0,long_cand_length):
                        j = i - 2 - k
                        if j > 0:
                            cand_long.insert(0, d['tokens'][j])
                            cand_long_index.insert(0, j)
                cand_long = ' '.join(cand_long)
                long_form = ""
                ## findBestLongForm
                if len(cand_long) > 0:
                    if left:
                        sIndex = len(t)-1
                        lIndex = len(cand_long)-1
                        while sIndex >= 0:
                            curChar = t[sIndex].lower()
                            if curChar.isdigit() or curChar.isalpha():
                                while (lIndex >= 0 and cand_long[lIndex].lower() != curChar) or (sIndex == 0 and lIndex > 0 and (cand_long[lIndex-1].isdigit() or cand_long[lIndex-1].isalpha())):
                                    lIndex -= 1
                                if lIndex < 0:
                                    break
                                lIndex -= 1
                            sIndex -= 1
                        if lIndex >= 0:
                            try:
                                lIndex = cand_long.rindex(" ", 0, lIndex+1)+1
                            except:
                                lIndex = 0
                            if cand_long:
                                cand_long = cand_long[lIndex:]
                                long_form = cand_long
                    else:
                        sIndex = 0
                        lIndex = 0
                        if t[0].lower() == cand_long[0].lower():
                            while sIndex < len(t):
                                curChar = t[sIndex].lower()
                                if curChar.isdigit() or curChar.isalpha():
                                    while (lIndex < len(cand_long) and cand_long[lIndex].lower() != curChar):
                                        lIndex += 1
                                    if lIndex >= len(cand_long):
                                        break
                                    lIndex += 1
                                sIndex += 1
                            if lIndex < len(cand_long):
                                try:
                                    lIndex = cand_long[lIndex:].index(" ")+lIndex+1
                                except:
                                    lIndex = len(cand_long)
                                if cand_long:
                                    cand_long = cand_long[:lIndex]
                                    long_form = cand_long
                    if long_form:
                        long_form = long_form.split()
                        if left:
                            long_form_index = cand_long_index[-len(long_form):]
                        else:
                            long_form_index = cand_long_index[:len(long_form)]
                        first = True
                        for j in range(len(d['tokens'])):
                            if j in long_form_index:
                                if first:
                                    pred['predictions'][j] = 'B-long'
                                    first = False
                                else:
                                    pred['predictions'][j] = 'I-long'
        predictions.append(pred)
    return predictions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str,
                        help='Path the the input file (e.g., dev.json)')
    parser.add_argument('-output', type=str,
                        help='Prediction file path')
    args = parser.parse_args()

    ## READ data
    with open(args.input) as file:
        data = json.load(file)

    ## Predict
    predictions = predict(data)

    ## Save
    with open(args.output, 'w') as file:
        json.dump(predictions, file)