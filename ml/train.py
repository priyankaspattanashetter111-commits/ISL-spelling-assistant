import json
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT/'data'/'samples.jsonl'
MODELS = ROOT/'ml'/'models'

def train():
    if not DATA.exists():
        raise ValueError('No samples. Collect real gestures in the Training tab first.')
    rows = [json.loads(x) for x in DATA.read_text().splitlines() if x.strip()]
    x = np.array([r['features'] for r in rows]); y = np.array([r['label'] for r in rows]); groups = np.array([r['session'] for r in rows])
    labels = sorted(set(y))
    if len(labels)<2:
        raise ValueError('Collect at least two labels; all 26 are required for full alphabet coverage.')
    for label in labels:
        indices = y==label
        if indices.sum()<30 or len(set(groups[indices]))<3:
            raise ValueError(f'{label}: need 30+ samples across at least 3 independent sessions.')
    # Seek a split with every label in all partitions, without sharing sessions.
    split = None
    for seed in range(100):
        trv, te = next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=seed).split(x,y,groups))
        tr0, va0 = next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed).split(x[trv],y[trv],groups[trv]))
        tr, va = trv[tr0], trv[va0]
        if all(set(y[idx])==set(labels) for idx in [tr,va,te]):
            split = tr,va,te; break
    if split is None:
        raise ValueError('Cannot make session-disjoint train/validation/test splits with all labels. Record more full-alphabet sessions (recommend 5+).')
    tr,va,te = split
    candidates = []
    for depth in [12,None]:
        model = RandomForestClassifier(n_estimators=200,max_depth=depth,class_weight='balanced',random_state=42,n_jobs=-1)
        model.fit(x[tr],y[tr]); candidates.append((accuracy_score(y[va],model.predict(x[va])),model))
    val, model = max(candidates,key=lambda p:p[0]); pred = model.predict(x[te])
    report = {'samples':len(rows),'labels':labels,'missing_alphabet':sorted(set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')-set(labels)),
              'validation_accuracy':val,'test_accuracy':accuracy_score(y[te],pred),'classification_report':classification_report(y[te],pred,output_dict=True,zero_division=0),
              'confusion_matrix':confusion_matrix(y[te],pred,labels=labels).tolist(),
              'split_counts':{'train':len(tr),'validation':len(va),'test':len(te)},
              'sessions':{k:sorted(set(groups[idx])) for k,idx in [('train',tr),('validation',va),('test',te)]},
              'note':'Random forest vote fractions are not calibrated probabilities. No epochs/loss curves apply.'}
    MODELS.mkdir(parents=True,exist_ok=True)
    joblib.dump({'model':model,'labels':labels,'feature_version':1},MODELS/'alphabet.joblib')
    (MODELS/'evaluation.json').write_text(json.dumps(report,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,8)); image=ax.imshow(report['confusion_matrix'],cmap='Blues');ax.set(xticks=range(len(labels)),yticks=range(len(labels)),xticklabels=labels,yticklabels=labels,xlabel='Predicted',ylabel='Actual',title='Held-out session confusion matrix');fig.colorbar(image,ax=ax);fig.tight_layout();fig.savefig(MODELS/'confusion-matrix.png');plt.close(fig)
    return report

if __name__=='__main__':
    print(json.dumps(train(),indent=2))
