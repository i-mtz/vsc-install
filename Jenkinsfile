// Jenkinsfile: scripted Jenkins pipefile
// This file was automatically generated using 'python -m vsc.install.ci'
// DO NOT EDIT MANUALLY

node {
    stage('checkout git') {
        checkout scm
    }
    stage('test') {
        sh 'python2.7 -V'
        sh 'python -m easy_install -U --user tox'
        sh 'export PATH=$HOME/.local/bin:$PATH && tox -v -c tox.ini'
    }
}
