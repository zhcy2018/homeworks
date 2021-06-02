import pandas as pd
import sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,precision_recall_fscore_support
from sklearn.metrics import classification_report
__ATTR_NAMES = ("duration",  # length (number of seconds) of the conn's
                # symbolic, type of the protocol, e.g. tcp, udp, etc.
                "protocol_type",
                # symbolic, network service on the destination, e.g., http, telnet, etc.
                "service",
                "flag",  # symbolic, normal or error status of the conn
                "src_bytes",  # number of data bytes from source to destination
                "dst_bytes",  # number of data bytes from destination to source
                "land",  # symbolic, 1 if conn is from/to the same host/port; 0 otherwise
                "wrong_fragment",  # number of ''wrong'' fragments 
                "urgent",  # number of urgent packets
                # ----------
                # ----- Basic features of individual TCP conn's -----
                # ----------
                "hot",  # number of ''hot'' indicators
                "num_failed_logins",  # number of failed login attempts 
                "logged_in",  # symbolic, 1 if successfully logged in; 0 otherwise
                "num_compromised",  # number of ''compromised'' conditions 
                "root_shell",  # 1 if root shell is obtained; 0 otherwise 
                "su_attempted",  # 1 if ''su root'' command attempted; 0 otherwise 
                "num_root",  # number of ''root'' accesses 
                "num_file_creations",  # number of file creation operations
                "num_shells",  # number of shell prompts 
                "num_access_files",  # number of operations on access control files
                "num_outbound_cmds",  # number of outbound commands in an ftp session 
                "is_host_login",  # symbolic, 1 if the login belongs to the ''hot'' list; 0 otherwise 
                "is_guest_login",  # symbolic, 1 if the login is a ''guest''login; 0 otherwise 
                # ----------
                # ----- Content features within a conn suggested by domain knowledge -----
                # ----------
                "count",  # number of conn's to the same host as the current conn in the past two seconds 
                # Time-based Traffic Features (examine only the conn in the past two seconds):
                # 1. Same Host, have the same destination host as the current conn
                # 2. Same Service, have the same service as the current conn.
                "srv_count",  # SH, number of conn's to the same service as the current conn
                "serror_rate",  # SH, % of conn's that have SYN errors
                "srv_serror_rate",  # SS, % of conn's that have SYN errors
                "rerror_rate",  # SH, % of conn's that have REJ errors 
                "srv_rerror_rate",  # SS, % of conn's that have REJ errors 
                "same_srv_rate",  # SH, % of conn's to the same service 
                "diff_srv_rate",  # SH, % of conn's to different services 
                "srv_diff_host_rate",  # SH,  % of conn's to different hosts 
                # ----------
                # Host-base Traffic Features, constructed using a window of 100 conn's to the same host
                "dst_host_count",
                "dst_host_srv_count",
                "dst_host_same_srv_rate",
                "dst_host_diff_srv_rate",
                "dst_host_same_src_port_rate",
                "dst_host_srv_diff_host_rate",
                "dst_host_serror_rate",
                "dst_host_srv_serror_rate",
                "dst_host_rerror_rate",
                "dst_host_srv_rerror_rate",
                # ----------
                # category
                "attack_type"
                )


def map2major5(df):
    d = {
        'normal.': 0,
        'ipsweep.': 1,
        'mscan.': 1,
        'nmap.': 1,
        'portsweep.': 1,
        'saint.': 1,
        'satan.': 1,
        'apache2.': 2,
        'back.': 2,
        'mailbomb.': 2,
        'neptune.': 2,
        'pod.': 2,
        'land.': 2,
        'processtable.': 2,
        'smurf.': 2,
        'teardrop.': 2,
        'udpstorm.': 2,
        'buffer_overflow.': 3,
        'loadmodule.': 3,
        'perl.': 3,
        'ps.': 3,
        'rootkit.': 3,
        'sqlattack.': 3,
        'xterm.': 3,
        'ftp_write.': 4,
        'guess_passwd.': 4,
        'httptunnel.': 3,  # disputation resolved
        'imap.': 4,
        'multihop.': 4,  # disputation resolved
        'named.': 4,
        'phf.': 4,
        'sendmail.': 4,
        'snmpgetattack.': 4,
        'snmpguess.': 4,
        'worm.': 4,
        'xlock.': 4,
        'xsnoop.': 4,
        'spy.': 4,
        'warezclient.': 4,
        'warezmaster.': 4  # disputation resolved
    }
    l = []
    for val in df['attack_type']:
        l.append(d[val])
    tmp_df = pd.DataFrame(l, columns=['attack_type'])
    df = df.drop('attack_type', axis=1)
    df = df.join(tmp_df)
    return df


def one_hot(df):
    service_one_hot = pd.get_dummies(df["service"])
    df = df.drop('service', axis=1)
    df = df.join(service_one_hot)
    
    if 'icmp' in df.columns:
        #训练集中含有此项，但是训练集没有，这样在预测时会出错，实验删除此项
        df = df.drop('icmp', axis=1)

    protocol_type_one_hot = pd.get_dummies(df["protocol_type"])
    df = df.drop('protocol_type', axis=1)
    df = df.join(protocol_type_one_hot)

    flag_type_one_hot = pd.get_dummies(df["flag"])
    df = df.drop('flag', axis=1)
    df = df.join(flag_type_one_hot)
    return df


def merge_sparse_feature(df):
    df.loc[(df['service'] == 'ntp_u')
           | (df['service'] == 'urh_i')
           | (df['service'] == 'tftp_u')
           | (df['service'] == 'red_i'), 'service'] = 'normal_service_group'

    df.loc[(df['service'] == 'pm_dump')
           | (df['service'] == 'http_2784')
           | (df['service'] == 'harvest')
           | (df['service'] == 'aol')
           | (df['service'] == 'http_8001'), 'service'] = 'satan_service_group'
    return df


def data_handle_first(filename):
    df = pd.read_csv(filename, header=None, names=__ATTR_NAMES)
    # sparse feature merge
    df = merge_sparse_feature(df)
    # one hot encoding
    df = one_hot(df)
    # y labels mapping
    df = map2major5(df)
    return df


def data_handle_sec():
    df1=data_handle_first('10pc')
    df2=data_handle_first('corrected')
    Y_tr = df1["attack_type"]
    X_tr = df1.drop("attack_type", axis=1)
    Y_te = df2["attack_type"]
    X_te = df2.drop("attack_type", axis=1)
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_tr)
    X_te = scaler.transform(X_te)
    
    return X_tr, Y_tr,X_te,Y_te


def train_and_test1():
    TR_X, TR_Y ,TE_X, TE_Y= data_handle_sec()
    print('handle complete')
    logreg = linear_model.LogisticRegression(C=1e5)
    logreg.fit(TR_X, TR_Y)
    print('train complete')
    pre = logreg.predict(TE_X)
    print(classification_report(pre,TE_Y))


def train_and_test2():
    TR_X, TR_Y,TE_X, TE_Y  = data_handle_sec()
    print('handle complete')
    logreg = MLPClassifier()
    logreg.fit(TR_X, TR_Y)
    print('train complete')
    pre = logreg.predict(TE_X)
    print(classification_report(pre,TE_Y))


def train_and_test3():
    TR_X, TR_Y,TE_X, TE_Y  = data_handle_sec()
    print('handle complete')
    logreg = KNeighborsClassifier()
    logreg.fit(TR_X, TR_Y)
    print('train complete')
    pre = logreg.predict(TE_X)
    print(classification_report(pre,TE_Y))


train_and_test3()