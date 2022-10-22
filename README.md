# gworkspace-client

Google Workspace를 편리하게 Python을 통해 제어할 수 있는 Client Class 패키지지로, google-api-python-client의 wrapper class를 패키지환 프로젝트입니다.

현재는 가장 쓰임새가 많은 GoogleDrive와 GoogleSheet를 지원합니다.

- [gworkspace-client](#gworkspace-client)
- [주요 기능](#주요-기능)
  - [공통 기능](#공통-기능)
  - [GoogleDrive](#googledrive)
  - [GoogleSheet](#googlesheet)
- [사용하기](#사용하기)
  - [1. 구글 Credentials 발급](#1-구글-credentials-발급)
  - [2. gworkspace-client 설치](#2-gworkspace-client-설치)
    - [github repo로부터 직접 설치하기](#github-repo로부터-직접-설치하기)
    - [Source Code를 Clone 후 설치하기](#source-code를-clone-후-설치하기)
  - [3. 클라이언트 객체 생성 및 사용하기](#3-클라이언트-객체-생성-및-사용하기)
    - [Prerequisite](#prerequisite)
    - [GoogleDrive](#googledrive-1)
    - [GoogleSheet](#googlesheet-1)
- [튜토리얼](#튜토리얼)
  - [GoogleDrive](#googledrive-2)
  - [GoogleSheet](#googlesheet-2)

# 주요 기능

## 공통 기능

* 토큰 생성: 구글 개발자 Credential을 기반으로 제어를 위한 토큰을 발행하고 업데이트합니다.
* 서비스 객체 생성: Google Workspace의 각 컴포넌트를 제어하기 위한 서비스 객체를 생성합니다.

## GoogleDrive
구글 드라이브를 제어하기 위해 아래와 같은 기능을 제공합니다.
* 폴더 생성: 특정 폴더 하위에 새로운 폴더를 생성할 수 있습니다.
* 파일 생성: 특정 폴더 하위에 새로운 파일(현재는 SpreadSheet 파일)을 생성할 수 있습니다.
* 파일 복사: 파일을 특정 위치(폴더)로 복사합니다.
* 파일 이동: 파일은 특정 위치(폴더)로 이동합니다.
* 폴더 목록 조회: 특정 위치(폴더) 하위의 폴더 목록을 조회합니다.
* 파일 목록 조회: 특정 위치(폴더) 하위의 파일 목록을 조회합니다.(폴더 제외)
* 파일 존재 유무 조회: 특정 위치(폴더) 하위에 특정 파일/폴더가 존재하는지 조회합니다.
* 파일 이름으로 찾기: 특정 위치(폴더) 하위에서 지정한 파일 이름과 일치하는 파일을 찾습니다.
* 파일 권한 생성/공유: 특정 파일에 특정 사용자의 권한(읽기, 쓰기, 커멘트)을 부여합니다.
* 파일 업로드: 특정 위치(폴더) 하위에 로컬 파일을 업로드합니다.
* 파일 다운로드: 지정한 파일을 로컬 파일로 다운로드하여 저장합니다.

## GoogleSheet
구글 시트를 제어하기 위해 아래와 같은 기능을 제공합니다.
* 시트 읽기: 특정 시트를 읽어서 pandas DataFrame 형태로 제공합니다.
* 시트 목록 조회: 구글 시트의 시트 목록을 조회합니다.
* 시트 추가: 구글 시트에 새로운 빈 워크시트를 추가합니다.
* 시트내 값 업데이트: 특정 워크시트내 범위를 지정하여 값을 변경합니다.
* 시트내 값 추가: 특정 워크시트내 범위를 지정하여 값을 추가합니다.
* 새로운 구글 시트 파일 생성: pandas DataFrame으로 구글 시트 파일을 특정 폴더 하위에 생성합니다.

# 사용하기

## 1. 구글 Credentials 발급
gworkspace-client를 사용하기 위해서는 아래의 링크를 참조하여 Google Developer Site에서 Credential을 받아야합니다.

1. Google Workspace 개발자를 위한 Authentication & Authorization 이해하기
* https://developers.google.com/workspace/guides/auth-overview

2. Python 용 Access Credential 발급
* https://developers.google.com/workspace/guides/create-credentials#desktop-app
* https://developers.google.com/drive/api/quickstart/python

위의 과정을 거쳐서 인증관련 토큰과 권한 파일을 받아서 보관해야합니다.

## 2. gworkspace-client 설치

### github repo로부터 직접 설치하기
```bash
$ pip install git+https://github.com/vanang/gworkspace-client.git#egg=gworkspace_client
```

### Source Code를 Clone 후 설치하기
```bash
$ git clone https://github.com/vanang/gworkspace-client.git
$ cd gworkspace-client
$ python setup.py install
```

## 3. 클라이언트 객체 생성 및 사용하기

### Prerequisite

* token file
* client secret file

### GoogleDrive
```python
from gworkspace_client.GoogleDrive import GoogleDrive

gdrive = GoogleDrive(token_path='../config/token.json',client_secret_path='../config/client_secret_...com.json' )

# creating a sub-folder
gdrive.create_folder(parent_folder_id='...', sub_folder_name='a_sub_folder')
```

### GoogleSheet

```python
from gworkspace_client.GoogleSheet import GoogleSheet 

gsheet = GoogleSheet(token_path='../config/token.json',client_secret_path='../config/client_secret_...com.json', sheet_url='...', sheet_id='...' )

# retrieving titles of sheets
titles = gsheet.get_sheet_titles()

# reading a sheet to pandas dataframe
df = gsheet.read_single_sheet(sheet_title=titles[0])
```
# 튜토리얼

## GoogleDrive

* [기본 GoogleDrive 사용법 튜토리얼](./notebooks/googledrive_tutorial.ipynb)

## GoogleSheet

* [기본 GoogleSheet 사용법 튜토리얼](./notebooks/googlesheet_tutorial.ipynb)
