Some Llamas enjoy statistics, so here's a new one.

There are many defensive rating statistics but how much does your defense affect your standings?
For example, let's say your opponent scored 6(3).  If you scored a 9(6) or a 0(0), your defense
does not matter.  However, if you scored a 4(4), your defense, combined with your opponent's
defense, changed a win into a loss.

I have also maintained that it helps to be hard to defend.  A hard to defend Llama I think is
someone who has no glaring weak field (relative to their other fields), and knows a smattering
of esoterica that they could possibly score a 3 on a hard question at any time.

So I have written a python script (publicly available in https://github.com/wusui/ll_new_defense_rating)
which calculates a new metric -- how many standings points is a player away from what would be expected
if scores were based only on how many questions one got right.  A running total over an entire season
reveals how much defense affected that person's rating.  The larger the number, the better as far
as the effect of defense is concerned.

For example, a match with a score of 5(4)-4(4) would be a tie based on just the total number of 
correct answers.  However, the player that scored 5 gets one more standings point and the player
that scored 4 gets one less standings point.

The math works out to be pretty simple.  Defense changing a loss to a win is worth +2 for the winner
and -2 for the loser.  Defense changing a tie to a win or a loss to a tie is worth +1 or -1.

So I checked all the players in the Pacific rundle for LL 78.  It appears that the individual with
the highest defensive rating has a rating of 8.  Looking at that individual's scores, he scored two
wins on what would have been losses 6(3)-4(4) and 5(3)-4(4), won three matches that would have been
ties 4(3)-3(3), 9(5)-8(5), and 7(4)-4(4), and converted one potential loss into a tie 4(2)-4(3).
Using this metric, this person also gave up 0 defensive rating points the entire season.
Those 8 standings points are the difference between 1st place and 7th place in the Pacific-B rundle.

This person also lead the rundle in DE (.821), lowest UfPA (17) and lowest PCAA (1.14).  So this new
statistic is pretty much in line with the other defensive statistics.

I maintain that this individual should be acknowledged as the Pacific Rundle's best defensive
player this season.

An now the moment that you have been waiting for, here are the results of running my script.

The highest defensive rating is: 8
    set by: usuiw

Wow! What a coincidence.  That person was me!  If I were crass enough to do so, I would recommend that
people should vote for me for the Sandra Trophy.

To be honest, I am crass enough to campaign for the Sandra Trophy.
