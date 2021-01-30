from process_ds import *
import numpy as np
from sklearn.metrics import f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def get_and_clean(dataset):
    df = pd.read_csv(
        dataset, usecols=['comment', 'Label'], encoding='unicode_escape')

    drop = []
    for index, row in df.iterrows():
        content = row['comment']
        translator = str.maketrans(
            string.punctuation, ' '*len(string.punctuation))
        content = content.translate(translator)
        content = preprocess(content)
        df.loc[index, 'comment'] = content
        if not df.loc[index, 'comment']:
            drop.append(index)
    df = df.drop(index=drop)
    return np.array(df['comment']), np.array(df['Label'])


def get_dataset():
    X_train, y_train = get_and_clean('dataset/train.csv')
    X_test, y_test = get_and_clean('dataset/test.csv')

        

    # vectorizer = TfidfVectorizer(max_features=8000)
    # X_train = vectorizer.fit_transform(X_train).toarray()
    # X_test = vectorizer.transform(X_test).toarray()

    # y_pred = nb(X_train, y_train, X_test, categorical=False)
    # print(f1_score(y_test, y_pred, average='micro'))

    # model = GaussianNB()
    # model.fit(X_train, y_train)
    # y_pred = model.predict(X_test)
    # print(f1_score(y_test, y_pred, average='micro'))


def nb(X_train, Y_train, X_test, categorical=False):
    if categorical:
        # count dist.
        df = X_train.groupby(Y_train)
        count = [df[c].value_counts() for c in X_train.columns]

        distinct_cols = [len(X_train[col].unique()) for col in X_train.columns]
    else:
        # collect means and standart deviations for gaussian distribution.
        means = X_train.groupby(Y_train).apply(np.mean)
        stds = X_train.groupby(Y_train).apply(np.std)

    # class distribution
    PCi = X_train.groupby(Y_train).apply(lambda x: len(x)) / X_train.shape[0]

    Y_pred = []
    for i in range(X_test.shape[0]):  # row iterate
        p = {}

        for Ci in np.unique(Y_train):  # class iterate
            p[Ci] = PCi.iloc[Ci]
            for j, val in enumerate(X_test.iloc[i]):  # column iterate
                if categorical:
                    # applying laplace smooth 1.
                    V = count[j][Ci].sum() + distinct_cols[j]
                    p[Ci] *= ((count[j][Ci, val] + 1)
                              if (Ci, val) in count[j] else 1) / V
                else:
                    p[Ci] *= g(val, means.iloc[Ci, j], stds.iloc[Ci, j])

        Y_pred.append(pd.Series(p).values.argmax())
    return Y_pred


get_dataset()
