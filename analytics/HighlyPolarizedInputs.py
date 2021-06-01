from sklearn import tree
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn import cluster
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.inspection import permutation_importance
from yellowbrick.target import FeatureCorrelation


sql_file = '../data/pitchfork.sqlite'
plot_loc = '../plots/'


def main():
    conn = sqlite3.connect(sql_file)

    print("# Display a table")
    query = "SELECT * FROM album_features;"
    album_features = pd.read_sql_query(query, conn)
    print(album_features)

    query = "SELECT reviewid, compound FROM sentiment;"
    print(f"\n{query}\n")
    df_sentiment = pd.read_sql_query(query, conn)
    print(df_sentiment)

    query = "SELECT reviewid, score FROM reviews;"
    print(f"\n{query}\n")
    df_review = pd.read_sql_query(query, conn)
    print(df_review)

    joined_table = album_features.merge(df_review)
    print(joined_table)

    X = joined_table.drop(["score", "reviewid"], axis=1)
    y = joined_table["score"]

    # Limit Data to just good and bad albums
    value_mask = (y > 8) | (y < 6)

    X = X.loc[value_mask]
    y = y.loc[value_mask]
    y = (y > 7)

    print("Percent Good Albums: {}".format(sum(y)/len(y)))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, random_state=123456)

    accuracy = pd.Series()
    importances = pd.DataFrame()

    importances["DecisionTree"], accuracy_score = DecisionTree(
        X_train, X_test, y_train, y_test)
    accuracy = accuracy.append(pd.Series([accuracy_score],
                                         index=['DecisionTree']))

    importances["LinearReg"], accuracy_score = LinearRegression(
        X_train, X_test, y_train, y_test)
    accuracy = accuracy.append(pd.Series([accuracy_score],
                                         index=['LinearReg']))

    importances["RandomForest"], accuracy_score = RandomForest(
        X_train, X_test, y_train, y_test)
    accuracy = accuracy.append(pd.Series([accuracy_score],
                                         index=['RandomForest']))

    print(importances)
    print()
    print(accuracy)

    plt.show()

    Correlations(X, y)


def plotStyle(ax, model_name):
    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    ax.set_title(f"Album Feature Importances Using {model_name}", loc="left")
    ax.set_xlabel('Importance')
    ax.set_ylabel('Album Feature')


def Correlations(X, y):

    visualizer = FeatureCorrelation(labels=X.columns)

    visualizer.fit(X, y)
    visualizer.show(
        outpath=f"{plot_loc}HighlyPolarized_Correlations.png", bbox_inches='tight')


def DecisionTree(X_train, X_test, y_train, y_test):

    model_name = "Decision Tree Classifier"
    model_key = "DecisionTree"

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X_train, y_train)

    predicted = clf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted)

    importances = permutation_importance(clf, X_train, y_train,
                                         n_repeats=30,
                                         random_state=0).importances_mean

    importances = pd.Series(importances, index=X_test.columns)

    importances = importances.sort_values(ascending=True)

    # Plot the figure.
    plt.figure(figsize=(12, 8))
    ax = importances.plot(kind='barh')

    plotStyle(ax, model_name)

    ax.set_title(f"Album Feature Importances Using {model_name}", loc="left")
    ax.set_xlabel('Importance')
    ax.set_ylabel('Album Feature')

    plt.figtext(.7, .3, f"Accuracy = {accuracy.round(4)}")
    plt.savefig(f"{plot_loc}HighlyPolarized_{model_key}_Importances.png",
                bbox_inches='tight')

    return importances, accuracy


def LinearRegression(X_train, X_test, y_train, y_test):

    model_name = "Linear Regression"
    model_key = "LinearRegression"

    linear = linear_model.Ridge(normalize=True, alpha=35)
    linear = linear.fit(X_train, y_train)

    predicted = linear.predict(X_test)
    accuracy = accuracy_score(y_test, predicted > .5)

    importances = permutation_importance(linear, X_train, y_train,
                                         n_repeats=30,
                                         random_state=0).importances_mean

    importances = pd.Series(importances, index=X_test.columns)
    importances = importances.sort_values(ascending=True)

    # Plot the figure.
    plt.figure(figsize=(12, 8))
    ax = importances.plot(kind='barh')

    plotStyle(ax, model_name)

    ax.set_title(f"Album Feature Importances Using {model_name}", loc="left")
    ax.set_xlabel('Importance')
    ax.set_ylabel('Album Feature')

    plt.figtext(.7, .3, f"Accuracy = {accuracy.round(4)}")
    plt.savefig(f"{plot_loc}HighlyPolarized_{model_key}_Importances.png",
                bbox_inches='tight')

    return importances, accuracy


def RandomForest(X_train, X_test, y_train, y_test):

    model_name = "Random Forest"
    model_key = "RandomForest"

    rf = RandomForestClassifier(
        n_estimators=100, oob_score=True, random_state=123456)

    rf = rf.fit(X_train, y_train)

    predicted = rf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted > .5)

    importances = permutation_importance(rf, X_test, y_test,
                                         n_repeats=30,
                                         random_state=0).importances_mean

    importances = pd.Series(importances, index=X_test.columns)
    importances = importances.sort_values(ascending=True)

    # Plot the figure.
    plt.figure(figsize=(12, 8))
    ax = importances.plot(kind='barh')

    plotStyle(ax, model_name)

    ax.set_title(f"Album Feature Importances Using {model_name}", loc="left")
    ax.set_xlabel('Importance')
    ax.set_ylabel('Album Feature')

    plt.figtext(.7, .3, f"Accuracy = {accuracy.round(4)}")
    plt.savefig(f"{plot_loc}HighlyPolarized_{model_key}_Importances.png",
                bbox_inches='tight')

    return importances, accuracy


if __name__ == "__main__":
    main()
