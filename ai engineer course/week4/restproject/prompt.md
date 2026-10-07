I am building a restaurant management AI agent system using Langgraph.

I will explain you very clearly and what i want and architecture. I will also explain you the nodes, states, edges. In the end i will give you test cases to simulate and to tell me whether they pass or not.

The rough plan is as follows:
There will be a user. When the code runs the user will give an order. This will be taken as input which i will type. This order should go to the llm. The order as of now should conatin dish and the required qunatity. 
For simplicity purpose for now we will limitthe order to one particular dish and whatever quantity the user wants.
the llm will extract the order name and quantity from user input.
if the  user input is unrelated to food ordering, the llm should not process and tel the user same thing that "i only take orders, i do not answer to general purpose".

Once llm is having order dish and qty, it will send that to a node called order_confirm.
the task of this order_confirm is to look at the menu(i wil tell you the menu)
Then this node decide one of the 3 cases- order confirmed->
order partially availaable means qty not sufficient
order not available at all-> not in menu or quantity zero 
It will put this info in status of state(i will tell u state content later)

Once llm receive this 
id status of order confirmed (full available) It should tell another node Cook.
if status partial or not availabkle it should again prompt the user to decide whether to place new order or confirm if they want to go ahead with partial order.

this order retrives limited to 3 attem pts only. the user still not satisfied , system came to an END.

when cook node calls, 2 cases arise
cooking done , status ready, next node is serve
cook faill, one more attempt use for cook probability function (40% chance of fail, 60% succeess).
the cook fails even after these then llm should say apology to user and come to END.

serve node also have 2 cases and 2 retry attempts
if serve fail two times then llm ashould say aplogy and END
if success the status become complete and llm tell user that your order completed

state of langgraph
associated message be llm and user
there should be order details
dish name as str
required quanitity as int
available quantity as str
order_confirm write the available quantity by reading the menu
llm should get to know order confirm status by reading the state
if dish not available in menu then orderconfirm should write 0 as avail quantity

then there should be status
each node will update the status as specified in the above rules 
then order retry attempts which are 3
 cook retry attempts which are 2
 serve retry attempts which are 2
 each time a failure happende and node is retrying it should decrement the counter
 if any retry counter becomes 0 it means it is over.LLm should understand whether it has to give a retry or issue apology by reading this counter
 in the end there should be final; result whether the order was completed or not

 Write the code and ask if there are any open questions from  your side then ask ,
 i will give you some test scenarios to test later on
