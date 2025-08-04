conda create -n open_manus python=3.12
conda activate open_manus
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus
pip install -r requirements.txt
cp config/config.example.toml config/config.toml
#打开config.toml配置，找官晴要配置文件
#配置完成后运行 python main.py
#之后输入prompt：Help me write a function for the Fibonacci sequence, execute the code, and record the return value. Finally, help me make an analysis document about the Fibonacci sequence, combine the code execution results, write it into a markdown file, and finally give me this file
#最后观察wanderful_medical_ai/workspace目录下是否生成相应文件，生成则说明项目初始化成功