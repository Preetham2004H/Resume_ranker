from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import pickle, os

class ResumeClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, X, y):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y,
                                                  random_state=42)
        self.model.fit(X_tr, y_tr)
        self.is_trained = True
        return {
            'train_acc': self.model.score(X_tr, y_tr),
            'test_acc':  self.model.score(X_te, y_te),
            'cv_mean':   cross_val_score(self.model, X, y, cv=5).mean(),
            'report':    classification_report(y_te, self.model.predict(X_te)),
            'cm':        confusion_matrix(y_te, self.model.predict(X_te)).tolist()
        }

    def predict(self, X):
        if not self.is_trained:
            raise ValueError('Model not trained')
        return self.model.predict(X)

    def save(self, path='model.pkl'):
        pickle.dump(self.model, open(path,'wb'))

    def load(self, path='model.pkl'):
        if not os.path.exists(path): raise FileNotFoundError(path)
        self.model = pickle.load(open(path,'rb')); self.is_trained = True
