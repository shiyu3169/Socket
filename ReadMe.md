#Socket

##Approach
This project is a simple socket project. I implemented a client program which communicates with a server using sockets. It only takes me few hours to make the code work, but I spend much more time to update it and learn from it. The first version of the project was just a main function doing everything linearly, which is hard to read and debug. After the code works, I seperated code into different functions to make it clean and easy to test. Next, I applied but Python's built-in arg-parse library to handle the command line inputs. It is much simpler and clear. Also, I applied regular expression library, re to parse the incoming message from server to make the application stronger and smarter. I believe this is the correct way to handle messages. 

##Challenges
The first challenge I met was learning Python. I only had few expierences of Python syntax and knowledge, so it takes me sometime to write my code. After that, I spent most of my time to find and understand its libraries, so I can use them to enhance my code.

##Testing
Initially I tested my code by running it with different inputs in Makefile. Then I wrote unite tests for each function to make sure every parts is working appropriately.

According to the requirements mentioned in Piazza (https://piazza.com/class/ixadkvtp7e41so?cid=44), I can only submit 4 files (client, readme, Makefile, secret_flag for this project. Test file available upon request.
