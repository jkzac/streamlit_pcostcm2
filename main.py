import streamlit as st
import pandas as pd
import numpy as np
import pickle
import boto3
from io import StringIO
from st_files_connection import FilesConnection
from datetime import datetime
import requests

st.set_page_config(
    page_title="PCOS Free",
    #page_icon=st.image('pcosfree.png'),
    layout="centered",
    initial_sidebar_state="expanded",)

# Main app logic
st.header('多囊卵巢综合征诊断及中医防治')
st.image('pcosmain.jpg')

###############
# Initialize session state for show_info if it does not exist
if 'show_info' not in st.session_state:
    st.session_state['show_info'] = 0
# Define a button and change the state on click
count=0
if st.button(":rainbow[什么是多囊卵巢综合征(PCOS)？]"):
    st.session_state['show_info'] += 1
    count = st.session_state['show_info']
# Display the info box based on the state
if count%2==1:
    st.info("多囊卵巢综合征（Polycystic Ovary Syndrome, PCOS）"
            "是育龄期女性最常见的内分泌代谢疾病，在育龄女性中的发病率为5-26%。"
            "影响女性的月经周期、生育，影响女性的外表及生活质量。"
            "糖尿病、高血压、心脏病和子宫内膜癌等远期并发症的发生风险也较正常人增加。"
            "多囊卵巢综合征的确切病因尚不清楚，但早期诊断和治疗加上减肥可以降低长期并发症的风险。")
################

tab1, tab2, tab3 = st.tabs(["PCOS自测诊断", "月经病中医证型识别", "PCOS图书馆"])

with tab1:
    # Title
    st.subheader("PCOS自测工具", anchor='self-test')

    with st.container(border=True):
        st.markdown(":blue[**临床表现**]")
        # Hyperandrogenism Section
        #Clinical sign + BMI (40)
        hirsutism = st.toggle("多毛症", help="毛发可能在以下位置过度生长：嘴唇、下巴、胸部、上背部、下背部、上腹部、下腹部、手臂和大腿。") * 10
        acne = st.toggle("油性皮肤和痤疮，以颜面部尤甚", help='痤疮根据皮损分布于颜面和胸背部、主要表现为白头、黑头粉刺、炎性丘疹、脓疱等多形性皮损等特点，临床易于诊断，通常无需做其他检查。') * 10
        hair_loss = st.toggle("脱发") * 10
        acanthosis_nigricans = st.toggle("黑棘皮症", help="黑棘皮症常在阴唇、颈背部、腋下、乳房下和腹股沟等皮肤皱褶部位出现灰褐色色素沉着，呈对称性，皮肤增厚，质地柔软。") * 10
        clinical_signs_score = hirsutism + acne + hair_loss + acanthosis_nigricans


    with st.container(border=True):
        #Biochemical sign (40)
        st.markdown(":blue[**理化特征**]")
        testosterone = st.toggle("睾酮(T)或游离睾酮水平升高", help='睾酮是由卵巢及肾上腺皮质分泌的雄烯二酮转化而来。主要功能是促进阴蒂、阴唇和阴阜的发育，促进阴毛、腋毛的生长，对雌激素有拮抗作用；对机体代谢功能有一定影响，如促进蛋白合成等。睾酮高多由多囊卵巢、高泌乳素血症、高胰岛素血症等内分泌疾病引发的，睾酮高严重危害女性身心健康，各位患者朋友尽早到医院做全面检查，对症治疗。') * 40
        dheas = st.toggle("硫酸脱氢表雄酮(DHEAS)水平升高") * 20
        biochemical_score = max(testosterone, dheas)
        hyperandrogenism_score = max(clinical_signs_score, biochemical_score)

        # Oligo-anovulation Section
        #st.header("排卵障碍", divider='gray')
        #st.subheader("血液检查")
        lh_fsh = st.toggle("黄体生成素(LH)/促卵泡激素(FSH)比值大于2") * 10
        progesterone = st.toggle("孕酮(P)水平低", help='由卵巢的黄体分泌，少量由肾上腺产生。主要功能是促使子宫内膜从增殖期转变为分泌期，为维持妊娠所必需。黄体酮临床用于先兆性流产、习惯性流产等闭经或闭经原因的反应性诊断等。') * 5
        estradiol = st.toggle("雌二醇(E2)水平低", help='主要由卵巢分泌，少量由肾上腺产生。主要功能是使子宫内膜生长成增殖期，促进女性第二性征的发育。如果仅出现雌二醇高的情况，则可能与排卵前、妊娠相关，但如果同时合并孕酮水平的升高，则考虑存在黄体功能不全或功能性子宫出血等疾病。') * 5
        amh = st.toggle("抗缪勒氏管激素(AMH)水平升高") * 5
        prolactin = st.toggle("催乳素(PRL)水平升高", help='由腺垂体分泌的一种多肽蛋白激素，主要功能是促进乳房发育及分泌乳汁。 生理的因素可以造成PRL高，比如妊娠、哺乳期，泌乳素可以因为应激、睡眠、体力活动、低血糖等原因升高，具体原因需要适当排查。') * 5
        blood_tests_score = lh_fsh + progesterone + estradiol + amh + prolactin

        # Polycystic Ovarian Morphology Section
        ovarian_morphology = st.toggle("超声显示多囊卵巢（单侧或双侧卵巢有≥12个卵泡，卵泡直径为2~9mm）") * 30

    with st.container(border=True):
        # Oligo-anovulation Section
        st.markdown(":blue[**月经情况**]")
        menstrual = st.toggle("月经周期不规律或闭经", help='不规律为周期<21或>35天, 或每年<8个周期。闭经指育龄期女性在排除怀孕的情况下出现无月经或月经突然停止6个月以上,或按自身原有月经周期停止3个周期以上。') * 30
        light_menses = st.toggle("月经量明显减少", help='月经总量为20～80ml之间。低于20ml为月经量偏少，月经量低于5ml则定义为月经过少。') * 15
        menstrual_cycle = max(menstrual, light_menses)

        oligo_anovulation_score = max(blood_tests_score, menstrual_cycle)

    # Calculating Total Score
    total_score = hyperandrogenism_score + oligo_anovulation_score + ovarian_morphology

    # Displaying Results
    if st.button("预测结果", type='primary'):
        if total_score >= 60:
            st.error(f"患有PCOS的可能性高，约为{total_score:.2f}%，请咨询专业医疗人员。")
            st.image('pcoshighrisk.jpg')
        elif total_score >= 30:
            st.warning(f"患有PCOS的可能性中等，约为{total_score:.2f}%，请咨询专业医疗人员。")
            st.image('pcosmediumrisk.jpg')
        else:
            st.success(f"患有PCOS的可能性低，约为{total_score:.2f}%，请咨询专业医疗人员。")
            st.image('pcoslowrisk.jpg')

with tab2:
    # Display a subheader
    st.markdown('**请输入您的信息:**')
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(":blue[**基本信息**]")
            姓名 = st.text_input("姓名", max_chars=50)
            年龄 = st.number_input("年龄(岁)", 18, 50)
            身高 = st.number_input("身高(cm)", 0, 200)
            体重 = st.number_input("体重(kg)", 0, 300)
            血型 = st.selectbox("血型", ['A型', 'B型', 'AB型', 'O型', '不清楚'])
            婚姻 = st.selectbox("婚姻", ['未婚', '已婚', '离异', '丧偶'])
            职业 = st.selectbox('职业', ['教育', '医药类', '公司职员', '自主创业', '家庭主妇', '在校生', '体力劳动者', '其他'])
            学历 = st.selectbox("教育经历", ['小学及以下', '中学', '大学本专科', '研究生'])


        with col2:
            st.write("")
            st.write("")
            st.write("")
            月经初潮 = st.number_input("月经初潮年龄(岁)", 0, 30)
            经期 = st.select_slider('经行天数', ['<3天', '3-4天', '5-7天', '8-14天', '>14天'])
            月经周期 = st.select_slider('月经周期', ['<28天', '28-35天', '36-60天', '61-90天', '>90天'])
            怀孕 = st.number_input("怀孕(次)", 0, 20)
            顺产 = st.number_input("顺产(次)", 0, 20)
            剖宫产 = st.number_input("剖宫产(次)", 0, 20)
            流产 = st.number_input("流产(次)", 0, 20)

    with st.container(border=True):
        col3, col4  = st.columns(2)
        with col3:
            st.markdown(":blue[**月经病专科问诊**]")
            #月经周期正常 = st.toggle("月经周期规律", help='正常月经的周期为21～35天，经期2～8天')
            月经周期提前 = st.toggle('月经周期提前', help='是指月经周期提前7天以上，甚至10余天一行，连续3个周期以上者。')
            月经周期延后 = st.toggle('月经周期延后', help='月经周期延后7天以上，甚至3到5个月，连续两个周期以上。')
            月经先后无定期 = st.toggle('月经先后无定期', help='月经不按正常周期来潮，时或提前，时或延后在7天以上，且连续三个月经周期者。')
            闭经 = st.toggle('闭经', help='闭经指育龄期女性在排除怀孕的情况下出现无月经或月经突然停止6个月以上,或按自身原有月经周期停止3个周期以上。')
            月经量 = st.select_slider("月经量（减少, 正常, 增加）", ['减少', '正常', '增加'], help='正常月经总量为20～80ml之间。低于20ml为月经量偏少，月经量低于5ml则定义为月经过少。月经量高于80ml则定义为月经过多。')
            月经色 = st.select_slider('月经色（淡红, 正常, 黑褐）', ['淡红', '正常', '黑褐'])
            月经质 = st.select_slider('月经质地（稀薄, 正常, 稠浓）', ['稀薄', '正常', '稠浓'])
            月经伴血块 = st.toggle('月经血块')

        with col4:
            经血崩漏 = st.toggle('经血崩漏')
            月经期乳房胀痛 = st.toggle('月经期乳房胀痛')
            月经期腹泻 = st.toggle('月经期腹泻')
            月经期情志异常 = st.toggle('月经期情志异常')
            痛经 = st.toggle('痛经', help='痛经指行经前后或月经期出现下腹部疼痛、坠胀，可伴有恶心、呕吐、腹泻、头晕、乏力等症状，严重时面色发白、出冷汗，或伴有腰酸或其他不适，症状严重影响生活质量。')
            痛经时腹坠痛空痛隐痛 = st.toggle('痛经时腹坠痛/空痛/隐痛')
            痛经时腹痛喜温喜按 = st.toggle('痛经时腹痛喜温喜按')
            贪食生冷或遇寒后加重月经不适 = st.toggle('贪食生冷或遇寒会加重月经不适')
            情绪失调时加重月经不适 = st.toggle('情绪失调时会加重月经不适')
            劳累后加重月经不适 = st.toggle('劳累后会加重月经不适')
            白带 = st.select_slider('白带（减少, 正常, 增加）', ['减少', '正常', '增加'])

    with st.container(border=True):
        col5, col6  = st.columns(2)
        with col5:
            st.markdown(":blue[**全身问诊**]")
            畏寒 = st.toggle('怕冷')
            畏热 = st.toggle('畏热')
            肢冷 = st.toggle('四肢冰凉')
            手足心热 = st.toggle('手足心热')
            潮热 = st.toggle('潮热')
            自汗 = st.toggle('自汗', help='白昼汗出，动则尤甚')
            盗汗 = st.toggle('盗汗', help='入睡后汗出异常，醒后汗泄即止')
            胸闷 = st.toggle('胸闷')
            乏力懒言 = st.toggle('乏力懒言')
            耳鸣 = st.toggle('耳鸣')
            喉中有痰 = st.toggle('喉中有痰')
            胁肋胀满 = st.toggle('胁肋胀满')
            胃脘胀满 = st.toggle('腹部胀满')
        with col6:
            胁肋胀满疼痛 = st.toggle('胁肋胀满/疼痛')
            腰膝酸软 = st.toggle('腰膝酸软')
            善叹息 = st.toggle('常叹息')
            纳呆 = st.toggle('胃口差')
            口干 = st.toggle('口干')
            口苦 = st.toggle('口苦')
            口渴喜饮 = st.toggle('口渴想喝水')
            口渴不欲饮或少饮 = st.toggle('口渴但不想喝水或少饮')
            失眠 = st.toggle('失眠', help='难以入睡，早醒，或侧夜不眠')
            多梦 = st.toggle('多梦')
            情志不遂 = st.toggle('情志不遂', help='急躁易怒，善惊易恐，善忧思，易紧张，压力大，抑郁，焦虑')
            基本不运动 = st.toggle('基本不运动', help='缺乏每周运动至少1次')
            多毛症 = st.toggle("多毛症状", help="毛发可能在以下位置过度生长：嘴唇、下巴、胸部、上背部、下背部、上腹部、下腹部、手臂和大腿。") * 10
            面部痤疮 = st.toggle("面部痤疮") * 10

    with st.container(border=True):
        col7, col8 = st.columns(2)
        with col7:
            st.markdown(":blue[**二便信息**]")
            便溏 = st.toggle('便溏')
            完谷不化 = st.toggle('完谷不化')
            晨起泄泻= st.toggle('晨起泄泻')
            便秘 = st.toggle('便秘')
        with col8:
            小便清长 = st.toggle('小便清长')
            小便黄赤 = st.toggle('小便黄赤')
            小便频数 = st.toggle('小便频数')
            小便量少 = st.toggle('小便量少')
            夜尿频多 = st.toggle('夜尿频多')

    with st.container(border=True):
        col9, col10  = st.columns(2)
        with col9:
            st.markdown(":blue[**舌象信息**]", help='若不清楚留空即可')
            胖舌 = st.toggle('舌形胖')
            舌齿痕 = st.toggle('舌边齿痕')
            舌裂纹 = st.toggle('舌有裂纹')
            舌点刺 = st.toggle('舌有点刺')
            舌瘀斑 = st.toggle('舌有瘀斑或瘀点')
        with col10:
            舌色 = st.select_slider('舌色（淡白, 淡红(正常), 红, 青紫, 不清楚）', ['淡白', '淡红(正常)', '红', '青紫', '不清楚'])
            舌苔白 = st.toggle('舌苔白')
            舌苔黄 = st.toggle('舌苔黄')
            舌苔腻 = st.toggle('舌苔腻')

    with st.container(border=True):
        col11, col12  = st.columns(2)
        with col11:
            st.markdown(":blue[**脉象信息**]", help='若不清楚留空即可')
            脉浮 = st.toggle('脉浮')
            脉沉 = st.toggle('脉沉')
            脉迟 = st.toggle('脉迟')
            脉数 = st.toggle('脉数')
        with col12:
            脉滑 = st.toggle('脉滑')
            脉细 = st.toggle('脉细')
            脉弦 = st.toggle('脉弦')
            脉涩 = st.toggle('脉涩')
            脉无力 = st.toggle('脉无力')

    with st.container(border=True):
        col13, col14  = st.columns(2)
        with col13:
            st.markdown(":blue[**既往病史**]")
            多囊 = st.toggle("多囊卵巢综合征")
            高血压 = st.toggle('高血压')
        with col14:
            高血脂 = st.toggle('高脂血症')
            糖尿病 = st.toggle('糖尿病')
            胰岛素抵抗 = st.toggle('胰岛素抵抗')

    #Mapping

    中学以下=0
    if 学历 == '中学':
        中学以下 = 0

    公司职员=0
    if 职业 == '公司职员':
        公司职员 = 1

    月经周期正常=0
    if ((月经周期提前==0)&(月经周期延后==0)&(月经先后无定期==0)&(闭经==0)):
        月经周期正常=1

    月经量明显增多 = 0
    if 月经量 == '增加':
        月经量明显增多 = 1

    月经色黯滞 = 0
    if 月经色 == '黑褐':
        月经色黯滞 = 1

    月经质稀薄=0
    if 月经质 == '稀薄':
        月经质稀薄 = 1

    带下量多 = 0
    if 白带 == '增加':
        带下量多 = 1

    舌色淡白 = 0
    if 舌色 == '淡白':
        舌色淡白 = 1

    舌色红 = 0
    if 舌色 == '红':
        舌色红 = 1

    青紫舌 = 0
    if 舌色 == '青紫':
        青紫舌 = 1

    # Button to trigger prediction
    if st.button("提交并预测证型", type='primary') == 1:

        if ((身高==0) | (体重==0) | (月经初潮==0)):
            with st.container(border=True):
                st.write('未完整输入资料！')

        else:
            BMI = 体重/((身高/100)**2)

            # Creating a feature list for the prediction model
            feature_list = [BMI, 中学以下, 公司职员, 月经初潮, 月经周期正常, 月经伴血块, 月经量明显增多, 月经色黯滞,
                             月经质稀薄, 月经期乳房胀痛, 月经期腹泻, 月经期情志异常, 痛经, 痛经时腹坠痛空痛隐痛,
                             痛经时腹痛喜温喜按, 劳累后加重月经不适, 贪食生冷或遇寒后加重月经不适, 情绪失调时加重月经不适, 带下量多, 肢冷,
                             畏寒, 手足心热, 胸闷, 耳鸣, 乏力懒言, 胃脘胀满, 善叹息, 胁肋胀满疼痛, 腰膝酸软,
                             纳呆, 口干, 口苦, 口渴喜饮, 口渴不欲饮或少饮, 失眠, 多梦, 情志不遂, 便溏, 便秘,
                             基本不运动, 胖舌, 舌裂纹, 舌齿痕, 舌瘀斑, 舌色淡白, 青紫舌, 舌色红, 舌苔白, 舌苔黄,
                             舌苔腻, 脉弦, 脉数, 脉沉, 脉细, 脉滑]

            # Reshaping the feature list into a format suitable for model input
            single_sample = np.array(feature_list).reshape(1, -1)

            # Load the model and make a prediction
            loaded_model = pickle.load(open('xgb_model.pkl', 'rb'))
            prediction = loaded_model.predict(single_sample)
            probabilities = loaded_model.predict_proba(single_sample)

            # Variables for probabilities
            肾阳虚证 = probabilities[0, 0]
            肾阴虚证 = probabilities[0, 1]
            痰湿证 = probabilities[0, 2]
            血瘀证 = probabilities[0, 3]
            气滞证 = probabilities[0, 4]

            ###############################################################################################
            ##Prepare to save user data
            # Get the current date and time
            录入时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Function to get user IP address
            def get_user_ip():
                try:
                    response = requests.get('https://api64.ipify.org?format=json')  # Get IP address using ipify API
                    return response.json()['ip']
                except Exception as e:
                    return 'IP not available'
            # Get user IP address
            用户IP = get_user_ip()

            column_names = ['录入时间', '用户IP','姓名', '年龄', '身高', '体重', '血型', '婚姻', '职业', '学历', '月经初潮', '经期', '月经周期', '怀孕', '顺产', '剖宫产', '流产',
                            '月经周期正常', '月经周期提前', '月经周期延后', '月经先后无定期', '闭经', '月经量',
                            '月经色', '月经质', '月经伴血块', '经血崩漏', '月经期乳房胀痛', '月经期腹泻', '月经期情志异常', '痛经', '痛经时腹坠痛空痛隐痛',
                            '痛经时腹痛喜温喜按', '贪食生冷或遇寒后加重月经不适', '情绪失调时加重月经不适', '劳累后加重月经不适', '白带', '畏寒', '畏热',
                            '肢冷', '手足心热', '潮热', '自汗', '盗汗', '胸闷', '乏力懒言', '耳鸣', '喉中有痰', '胁肋胀满', '胃脘胀满', '胁肋胀满疼痛', '腰膝酸软',
                            '善叹息', '纳呆', '口干', '口苦', '口渴喜饮', '口渴不欲饮或少饮', '失眠', '多梦', '情志不遂', '基本不运动', '多毛症', '面部痤疮', '便溏', '完谷不化',
                            '晨起泄泻', '便秘', '小便清长', '小便黄赤', '小便频数', '小便量少', '夜尿频多', '胖舌', '舌齿痕', '舌裂纹', '舌点刺', '舌瘀斑', '舌色', '舌苔白',
                            '舌苔黄', '舌苔腻', '脉浮', '脉沉', '脉迟', '脉数', '脉滑', '脉细', '脉弦', '脉涩', '脉无力', '多囊', '高血压', '高血脂', '糖尿病', '胰岛素抵抗',
                            '肾阳虚证', '肾阴虚证', '痰湿证', '血瘀证', '气滞证']

            save_list = [录入时间, 用户IP, 姓名, 年龄, 身高, 体重, 血型, 婚姻, 职业, 学历, 月经初潮, 经期, 月经周期, 怀孕, 顺产, 剖宫产, 流产,
                         月经周期正常, 月经周期提前, 月经周期延后, 月经先后无定期, 闭经, 月经量,
                         月经色, 月经质, 月经伴血块, 经血崩漏, 月经期乳房胀痛, 月经期腹泻, 月经期情志异常, 痛经, 痛经时腹坠痛空痛隐痛,
                         痛经时腹痛喜温喜按, 贪食生冷或遇寒后加重月经不适, 情绪失调时加重月经不适, 劳累后加重月经不适, 白带, 畏寒, 畏热,
                         肢冷, 手足心热, 潮热, 自汗, 盗汗, 胸闷, 乏力懒言, 耳鸣, 喉中有痰, 胁肋胀满, 胃脘胀满, 胁肋胀满疼痛, 腰膝酸软,
                         善叹息, 纳呆, 口干, 口苦, 口渴喜饮, 口渴不欲饮或少饮, 失眠, 多梦, 情志不遂, 基本不运动, 多毛症, 面部痤疮, 便溏, 完谷不化,
                         晨起泄泻, 便秘, 小便清长, 小便黄赤, 小便频数, 小便量少, 夜尿频多, 胖舌, 舌齿痕, 舌裂纹, 舌点刺, 舌瘀斑, 舌色, 舌苔白,
                         舌苔黄, 舌苔腻, 脉浮, 脉沉, 脉迟, 脉数, 脉滑, 脉细, 脉弦, 脉涩, 脉无力, 多囊, 高血压, 高血脂, 糖尿病, 胰岛素抵抗,
                         肾阳虚证, 肾阴虚证, 痰湿证, 血瘀证, 气滞证]

            # Create a DataFrame from the save_list
            df_user = pd.DataFrame([save_list], columns=column_names)

            # Identify the boolean columns and convert them to binary (1/0)
            bool_columns = df_user.select_dtypes(include='bool').columns  # Select columns with boolean type
            df_user[bool_columns] = df_user[bool_columns].astype(int)     # Convert boolean to binary (1/0)

            # Create connection object and retrieve file contents from AWS S3.
            # Specify input format is a csv and to cache the result for 5 seconds.
            conn = st.connection('s3', type=FilesConnection)
            df = conn.read("jkawsbucketstreamlit/user_data.csv", input_format="csv", ttl=5)

            # Concatenate the new row to the existing DataFrame
            df = pd.concat([df, df_user], ignore_index=True)

            # Convert DataFrame to CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)

            # Upload the CSV back to S3
            s3 = boto3.client('s3')
            bucket_name = "jkawsbucketstreamlit"
            file_name = "user_data.csv"

            s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
            ###############################################################################################

            #Display name and intro
            st.write(f":blue[**{姓名}**]女士您好！您的诊断结果如下：")

            # Display results based on the prediction
            if prediction[0,0] == 1:
                col1, col2 = st.columns([1.5,2.5])
                with col1:
                    st.success(f' {probabilities[0, 0]*100:.2f}%诊断为肾阳虚证')
                with col2:
                    with st.expander(":blue[认识肾阳虚证]"):
                        st.info('在中医理论中，肾阳虚指的是肾脏阳气不足，肾主生殖，为先天之本，若先天禀赋不足，或早婚房劳伤肾，致肾阳虚衰，脾阳根于肾阳，命门火衰，阳气不达，表现为卵巢功能减弱，影响卵泡的成熟和排卵，肾阳虚可能导致代谢率下降，进而影响体重和胰岛素抵抗，这些都是PCOS患者常见的问题。')
                        st.info(':black[**食疗**：应选择温补肾阳的食物，如羊肉、韭菜、胡桃、桂圆等。]'
                             ':black[**运动疗法**：适合进行温和的运动，如散步、太极拳，注意避免过度劳累。]'
                             ':black[**针灸疗法**：关注肾俞穴、命门穴等。]')
            if prediction[0,1] == 1:
                col1, col2 = st.columns([1.5,2.5])
                with col1:
                    st.success(f' {probabilities[0, 1]*100:.2f}%诊断为肾阴虚证')
                with col2:
                    with st.expander(":blue[认识肾阴虚证]"):
                        st.info('中医认为肾藏精，与生殖功能密切相关。肾阴虚可能导致生殖系统的滋养和润泽不足，影响卵巢的正常功能，包括卵泡的成熟和排卵。此外，由于体内阴阳失衡，进而影响内分泌系统，包括性激素的平衡。这种内分泌失衡可能导致或加剧PCOS的症状，如月经不规律、排卵障碍和多囊卵巢。')
                        st.info(':black[**食疗**：宜食用滋阴润燥的食物，如黑芝麻、桑葚、猪肾、豆腐等。]'
                                ':black[**运动疗法**：推荐太极拳、八段锦、瑜伽等温和的运动。]'
                                ':black[**针灸疗法**：可以选择肾俞穴、太溪穴等穴位进行调理。]')
            if prediction[0,2] == 1:
                col1, col2 = st.columns([1.5,2.5])
                with col1:
                    st.success(f' {probabilities[0, 2]*100:.2f}%诊断为痰湿证')
                with col2:
                    with st.expander(":blue[认识痰湿证]"):
                        st.info('在中医学中，痰湿证是由于患者或素体肥胖，或过食膏粱厚味，痰湿内生或寒湿之邪内侵，酿而成痰，痰湿阻滞胞脉，冲任受损而发病。脾为后天之本，痰湿证与脾脏密不可分，脾主管消化吸收，运化水谷，但当脾虚湿阻时，水湿无法代谢，使身体内的水液代谢紊乱，最终导致内分泌失调，于是就会表现为多囊卵巢综合征。其发病机理可以从内分泌和代谢失调、 肥胖和胰岛素抵抗、卵巢微环境的改变、激素代谢障碍几个方面来理解。')
                        st.info(':black[**食疗**：应选择健脾利湿的食物，如薏米、扁豆、苦瓜、冬瓜等。]'
                                ':black[**运动疗法**：建议进行有氧运动，如快走、慢跑、游泳等，以促进代谢。]'
                                ':black[**针灸疗法**：针对脾经上的穴位如足三里穴、阴陵泉穴进行调理。]')
            if prediction[0,3] == 1:
                col1, col2 = st.columns([1.5,2.5])
                with col1:
                    st.success(f' {probabilities[0, 3]*100:.2f}%诊断为血瘀证')
                with col2:
                    with st.expander(":blue[认识血瘀证]"):
                        st.info('在中医理论中，导致血瘀证的因素有很多，如气滞、气虚、寒凝、外伤等，在PCOS中，血瘀证以气滞血瘀多见，由于气血不利，瘀阻胞宫而发病。研究表明，血瘀可能会导致卵巢微循环障碍，妨碍卵泡的正常成熟和排卵，导致卵泡发育不全和囊肿形成，加剧PCOS症状；同时，血瘀可能扰乱内分泌系统，尤其影响性激素平衡，影响月经周期和排卵。长期的血瘀可能导致局部炎症反应，这种慢性炎症状态同样会影响卵巢的正常生理功能。')
                        st.info(':black[**食疗**：推荐活血化瘀的食物，如红枣、桃仁、红花、土豆等。]'
                                ':black[**运动疗法**：适宜进行温和的伸展运动和散步，避免剧烈运动。]'
                                ':black[**针灸疗法**：重点是调理血脉，可选择血海穴、三阴交穴等穴位。]')
            if prediction[0,4] == 1:
                col1, col2 = st.columns([1.5,2.5])
                with col1:
                    st.success(f' {probabilities[0, 4]*100:.2f}%诊断为气滞证')
                with col2:
                    with st.expander(":blue[认识气滞证]"):
                        st.info('中医认为，气为血之帅，血为气之母，气滞则血行不利。情志直接影响气血的运行，情绪不稳定，如压力、焦虑或抑郁，可导致气滞，气滞又进一步影响内分泌系统，可能导致或加剧PCOS的症状，如月经不规律和排卵障碍。此外，在中医理论中，肝脏负责疏泄，从而保证气血的正常运行，因此，气滞常常与“肝郁”（肝脏功能紊乱）相联系，这可能导致激素失衡，影响卵巢功能，进而引发或加重PCOS。')
                        st.info(':black[**食疗**：应选择能疏肝理气的食物，如柑橘、香菜、玫瑰花茶、薄荷等。]'
                                ':black[**运动疗法**：适合进行有氧运动，如快走、慢跑、太极拳，以及瑜伽的呼吸调节。]'
                                ':black[**针灸疗法**：针对肝经上的穴位如太冲穴、期门穴进行调理。]')
            if ((prediction[0,0]!= 1)&(prediction[0,1]!= 1)&(prediction[0,2]!= 1)&(prediction[0,3]!=1)&(prediction[0,4]!=1)):
                st.success("您被诊断为肾阳虚证、肾阴虚证、痰湿证、血瘀证或气滞证的可能性低。")

with tab3:
    #st.image("pcoslibrary.jpg")

    ##多囊常见证型
    with st.expander(":blue[**多囊卵巢综合征常见哪种证型？**]"):
        data = pd.read_csv('df_pcos_clean.csv')
        # Calculate the percentages
        columns_to_analyze = ['肾阴虚证', '肾阳虚证', '痰湿证', '血瘀证', '气滞证']
        percentages = (data[columns_to_analyze].sum() / len(data)) * 100
        st.bar_chart(percentages)

    #认识证型
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    if col_c.button("认识肾阳虚证"):
        st.info('**肾阳虚证**：在中医理论中，肾阳虚指的是肾脏阳气不足，肾主生殖，为先天之本，若先天禀赋不足，或早婚房劳伤肾，致肾阳虚衰，脾阳根于肾阳，命门火衰，阳气不达，表现为卵巢功能减弱，影响卵泡的成熟和排卵，肾阳虚可能导致代谢率下降，进而影响体重和胰岛素抵抗，这些都是PCOS患者常见的问题。')
        st.info(':black[**食疗**：应选择温补肾阳的食物，如羊肉、韭菜、胡桃、桂圆等。]'
                ':black[**运动疗法**：适合进行温和的运动，如散步、太极拳，注意避免过度劳累。]'
                ':black[**针灸疗法**：关注肾俞穴、命门穴等。]')
    if col_d.button("认识肾阴虚证"):
        st.info('**肾阴虚证**：中医认为肾藏精，与生殖功能密切相关。肾阴虚可能导致生殖系统的滋养和润泽不足，影响卵巢的正常功能，包括卵泡的成熟和排卵。此外，由于体内阴阳失衡，进而影响内分泌系统，包括性激素的平衡。这种内分泌失衡可能导致或加剧PCOS的症状，如月经不规律、排卵障碍和多囊卵巢。')
        st.info(':black[**食疗**：宜食用滋阴润燥的食物，如黑芝麻、桑葚、猪肾、豆腐等。]'
                ':black[**运动疗法**：推荐太极拳、八段锦、瑜伽等温和的运动。]'
                ':black[**针灸疗法**：可以选择肾俞穴、太溪穴等穴位进行调理。]')
    if col_b.button("认识痰湿证"):
        st.info('**痰湿证**：在中医学中，痰湿证是由于患者或素体肥胖，或过食膏粱厚味，痰湿内生或寒湿之邪内侵，酿而成痰，痰湿阻滞胞脉，冲任受损而发病。脾为后天之本，痰湿证与脾脏密不可分，脾主管消化吸收，运化水谷，但当脾虚湿阻时，水湿无法代谢，使身体内的水液代谢紊乱，最终导致内分泌失调，于是就会表现为多囊卵巢综合征。其发病机理可以从内分泌和代谢失调、 肥胖和胰岛素抵抗、卵巢微环境的改变、激素代谢障碍几个方面来理解。')
        st.info(':black[**食疗**：应选择健脾利湿的食物，如薏米、扁豆、苦瓜、冬瓜等。]'
                ':black[**运动疗法**：建议进行有氧运动，如快走、慢跑、游泳等，以促进代谢。]'
                ':black[**针灸疗法**：针对脾经上的穴位如足三里穴、阴陵泉穴进行调理。]')
    if col_e.button("认识血瘀证"):
        st.info('**血瘀证**：在中医理论中，导致血瘀证的因素有很多，如气滞、气虚、寒凝、外伤等，在PCOS中，血瘀证以气滞血瘀多见，由于气血不利，瘀阻胞宫而发病。研究表明，血瘀可能会导致卵巢微循环障碍，妨碍卵泡的正常成熟和排卵，导致卵泡发育不全和囊肿形成，加剧PCOS症状；同时，血瘀可能扰乱内分泌系统，尤其影响性激素平衡，影响月经周期和排卵。长期的血瘀可能导致局部炎症反应，这种慢性炎症状态同样会影响卵巢的正常生理功能。')
        st.info(':black[**食疗**：推荐活血化瘀的食物，如红枣、桃仁、红花、土豆等。]'
                ':black[**运动疗法**：适宜进行温和的伸展运动和散步，避免剧烈运动。]'
                ':black[**针灸疗法**：重点是调理血脉，可选择血海穴、三阴交穴等穴位。]')
    if col_a.button("认识气滞证"):
        st.info('**气滞证**：中医认为，气为血之帅，血为气之母，气滞则血行不利。情志直接影响气血的运行，情绪不稳定，如压力、焦虑或抑郁，可导致气滞，气滞又进一步影响内分泌系统，可能导致或加剧PCOS的症状，如月经不规律和排卵障碍。此外，在中医理论中，肝脏负责疏泄，从而保证气血的正常运行，因此，气滞常常与“肝郁”（肝脏功能紊乱）相联系，这可能导致激素失衡，影响卵巢功能，进而引发或加重PCOS。')
        st.info(':black[**食疗**：应选择能疏肝理气的食物，如柑橘、香菜、玫瑰花茶、薄荷等。]'
                ':black[**运动疗法**：适合进行有氧运动，如快走、慢跑、太极拳，以及瑜伽的呼吸调节。]'
                ':black[**针灸疗法**：针对肝经上的穴位如太冲穴、期门穴进行调理。]')

    ##性激素六项基本释义
    with st.expander(":blue[**性激素六项基本释义**]"):
        st.write('**01 卵泡刺激素（FSH）**')
        st.write('是由腺垂体分泌的一种糖蛋白激素，生理作用主要是促进卵泡发育、成熟及分泌雌激素。 高FSH水平可能表明卵巢储备减少，或者剩下的卵子较少，FSH水平会影响生育治疗的成功。 在女性的正常生育年限中，FSH在1.7-8.5mu/mI之间，当FSH浓度超过10，这说明卵巢功能有衰退的迹象，如果超过15则意味着卵巢失去排卵功能，要尽快针对性治疗并通过试管婴儿方式治疗。')
        st.write('**02 黄体生成激素（LH）**')
        st.write('是由腺垂体分泌的一种糖蛋白激素。生理作用主要是促进女性排卵和黄体生成，促进黄体分泌孕激素和雌激素。促黄体生成素升高，主要是由于内分泌功能紊乱导致的，在临床上常见于多囊卵巢综合征，卵巢功能衰退，更年期综合症等情况。')
        st.write('**03 催乳素（PRL）**')
        st.write('由腺垂体分泌的一种多肽蛋白激素，主要功能是促进乳房发育及分泌乳汁。 生理的因素可以造成PRL高，比如妊娠、哺乳期，泌乳素可以因为应激、睡眠、体力活动、低血糖等原因升高，具体原因需要适当排查。')
        st.write('**04 雌二醇（E2）**')
        st.write('主要由卵巢分泌，少量由肾上腺产生。主要功能是使子宫内膜生长成增殖期，促进女性第二性征的发育。如果仅出现雌二醇高的情况，则可能与排卵前、妊娠相关，但如果同时合并孕酮水平的升高，则考虑存在黄体功能不全或功能性子宫出血等疾病。')
        st.write('**05 孕酮（P）**')
        st.write('由卵巢的黄体分泌，少量由肾上腺产生。主要功能是促使子宫内膜从增殖期转变为分泌期，为维持妊娠所必需。黄体酮临床用于先兆性流产、习惯性流产等闭经或闭经原因的反应性诊断等。')
        st.write('**06 睾酮（T）**')
        st.write('是由卵巢及肾上腺皮质分泌的雄烯二酮转化而来。主要功能是促进阴蒂、阴唇和阴阜的发育，促进阴毛、腋毛的生长，对雌激素有拮抗作用；对机体代谢功能有一定影响，如促进蛋白合成等。睾酮高多由多囊卵巢、高泌乳素血症、高胰岛素血症等内分泌疾病引发的，睾酮高严重危害女性身心健康，各位患者朋友尽早到医院做全面检查，对症治疗。')

    ##性激素六项在不同检查时间的不同意义
    with st.expander(":blue[**性激素六项在不同检查时间的不同意义**]"):
        st.write('检查内分泌最好在月经来潮的第三天。但对于月经长期不来潮而且又急于了解检查结果者，则随时可以检查，这个时间就默认为月经前的时间，其结果也就参照黄体期的检查结果。')
        st.write('对于性激素六项的检查，要区分两个检查时间的不同检查内容：')
        st.write('1、月经第2、3天（月经期）激素检查：关注卵巢储备和基础内分泌水平。')
        st.write('2、月经第12、13天（排卵期）激素检查：关注卵泡的生长成熟和排卵情况。')
        st.write('月经第2、3天的检查')
        st.write('(1) 基础FSH高于10提示卵巢储备不良：结合AMH水平和患者年龄可以预估卵子储备数量。FSH高见于卵巢早衰、卵巢不敏感综合征、原发性闭经等。FSH高于40mIU/ml，则对克罗米芬之类的促排卵药无效。')
        st.write('(2) 基础E2在50pg/ml以下正常：因为E2和FSH是负反馈，即使基础FSH低于10，但是E2高于50pg/ml同样有可能卵巢储备不良。')
        st.write('(3) LH低于5mIU/ml提示促性腺激素功能不足：高FSH如再加高LH，则卵巢功能衰竭迹象非常明显。LH/FSH≥3则是诊断多囊卵巢综合征的依据之一。')
        st.write('(4) PRL高于17.6ng/ml为高催乳素血症：过多的催乳素可抑制FSH及LH的分泌，抑制卵巢功能，抑制排卵。')
        st.write('(5) 睾酮即血T值高：高睾酮血症也可引起不孕。患多囊卵巢综合征时，血T值也增高，多毛，并伴有痤疮、脂溢和脱发。')
        st.write('月经第12、13天的检查')
        st.write('(1) LH峰值判断排卵：看有无排卵前LH峰值及判断是否接近/或已排卵，排卵试纸就是LH试纸。')
        st.write('(2) E2高低判断卵泡质量和成熟时间：一般情况下一颗成熟卵泡有150以上的雌激素作为支撑，以此判断取卵和注射HCG卵泡催熟针剂的时间。当卵泡大小到达18以上，但是雌激素小于150时，视为雌激素偏低，有空泡或者卵子质量不好的可能性。')
        st.write('(3) 孕酮低可能出现排卵期出血：排卵后期血孕酮值低，见于黄体功能不全、排卵型功能失调性子宫出血等。')
