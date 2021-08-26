#!/bin/bash

export VP=VP10

export MIT=_mit_
export WITH=_with_
export OHNE=_ohne_
export WITHOUT=_without_
export SPLINE_MIT=_spline_mit_
export SPLINE_WITH=_spline_with_
export SPLINE_OHNE=_spline_ohne_
export SPLINE_WITHOUT=_spline_without_


export count=1
mv $VP/$VP$MIT$count $VP/$VP$WITH$count
echo "mv $VP/$VP$MIT$count to $VP/$VP$WITH$count"

export count=2
mv $VP/$VP$MIT$count $VP/$VP$WITH$count
echo "mv $VP/$VP$MIT$count to $VP/$VP$WITH$count"

export count=3
mv $VP/$VP$MIT$count $VP/$VP$WITH$count
echo "mv $VP/$VP$MIT$count to $VP/$VP$WITH$count"

export count=1
mv $VP/$VP$OHNE$count $VP/$VP$WITHOUT$count
echo "mv $VP/$VP$OHNE$count to $VP/$VP$WITHOUT$count"

export count=2
mv $VP/$VP$OHNE$count $VP/$VP$WITHOUT$count
echo "mv $VP/$VP$OHNE$count to $VP/$VP$WITHOUT$count"

export count=1
mv $VP/$VP$SPLINE_MIT$count $VP/$VP$SPLINE_WITH$count
echo "mv $VP/$VP$SPLINE_MIT$count to $VP/$VP$WITH$count"

export count=2
mv $VP/$VP$SPLINE_MIT$count $VP/$VP$SPLINE_WITH$count
echo "mv $VP/$VP$SPLINE_MIT$count to $VP/$VP$WITH$count"

export count=3
mv $VP/$VP$SPLINE_MIT$count $VP/$VP$SPLINE_WITH$count
echo "mv $VP/$VP$SPLINE_MIT$count to $VP/$VP$WITH$count"

export count=1
mv $VP/$VP$SPLINE_OHNE$count $VP/$VP$SPLINE_WITHOUT$count
echo "mv $VP/$VP$SPLINE_OHNE$count to $VP/$VP$SPLINE_WITHOUT$count"

export count=2
mv $VP/$VP$SPLINE_OHNE$count $VP/$VP$SPLINE_WITHOUT$count
echo "mv $VP/$VP$SPLINE_OHNE$count to $VP/$VP$SPLINE_WITHOUT$count"
