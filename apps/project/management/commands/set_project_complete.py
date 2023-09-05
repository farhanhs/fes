# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
from optparse import make_option
from fishuser.models import *
from django.conf import settings


def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"將101年度(含)以下的工程接設定為已結案   --year=101 --date=2016-12-31"
    option_list = BaseCommand.option_list + (
        make_option('--year', action='store', help='year', default=None),
        make_option('--date', action='store', help='date', default=None),
    )

    def handle(self, *args, **kw):
        # year = kw['year']
        # date = kw['date']
        # projects = Project.objects.filter(year__lte=year)
        # for obo in CountyChaseProjectOneByOne.objects.filter(project__in=projects.filter(purchase_type__value__in=[u'工程', u'工程勞務']), act_eng_do_closed__isnull=True):
        #     obo.act_eng_do_closed = date
        #     obo.save()

        # for obo in CountyChaseProjectOneByOne.objects.filter(project__in=projects.filter(purchase_type__value=u'一般勞務'), act_ser_acceptance_closed__isnull=True):
        #     obo.act_ser_acceptance_closed = date
        #     obo.save()

        c_list = [ [1793, '2017-12-31'] , [1615, '2016-12-31'] , [1617, '2016-12-31'] , [1742, '2016-12-31'] , [1619, '2016-12-31'] , [1616, '2016-12-31'] , [1682, '2016-12-31'] , [1675, '2016-12-31'] , [1636, '2016-12-31'] , [1673, '2016-12-31'] , [1623, '2016-12-31'] , [1714, '2016-12-31'] , [1702, '2016-12-31'] , [1700, '2016-12-31'] , [1670, '2016-12-31'] , [1688, '2016-12-31'] , [1689, '2016-12-31'] , [1690, '2016-12-31'] , [1678, '2016-12-31'] , [1679, '2016-12-31'] , [1680, '2016-12-31'] , [1681, '2016-12-31'] , [1677, '2016-12-31'] , [1676, '2016-12-31'] , [1691, '2016-12-31'] , [1694, '2016-12-31'] , [1697, '2016-12-31'] , [1739, '2016-12-31'] , [1740, '2016-12-31'] , [1741, '2016-12-31'] , [1719, '2016-12-31'] , [1718, '2016-12-31'] , [1712, '2016-12-31'] , [1760, '2016-12-31'] , [1699, '2016-12-31'] , [1748, '2016-12-31'] , [1736, '2016-12-31'] , [1737, '2016-12-31'] , [1752, '2016-12-31'] , [1753, '2016-12-31'] , [1732, '2016-12-31'] , [1730, '2016-12-31'] , [1731, '2016-12-31'] , [1744, '2016-12-31'] , [1754, '2016-12-31'] , [1901, '2016-12-31'] , [1757, '2016-12-31'] , [1672, '2016-12-31'] , [1622, '2016-12-31'] , [1624, '2016-12-31'] , [1685, '2016-12-31'] , [1735, '2016-12-31'] , [1635, '2016-12-31'] , [1671, '2016-12-31'] , [1716, '2016-12-31'] , [1701, '2016-12-31'] , [1903, '2016-12-31'] , [1758, '2016-12-31'] , [1759, '2016-12-31'] , [1902, '2016-12-31'] , [1704, '2016-12-31'] , [1703, '2016-12-31'] , [1684, '2016-12-31'] , [1717, '2016-12-31'] , [1900, '2016-12-31'] , [1698, '2016-12-31'] , [1743, '2016-12-31'] , [1729, '2016-12-31'] , [1755, '2016-12-31'] , [1509, '2015-12-31'] , [1525, '2015-12-31'] , [1487, '2015-12-31'] , [1490, '2015-12-31'] , [1508, '2015-12-31'] , [1488, '2015-12-31'] , [1535, '2015-12-31'] , [1524, '2015-12-31'] , [1533, '2015-12-31'] , [1365, '2015-12-31'] , [1517, '2015-12-31'] , [1532, '2015-12-31'] , [1530, '2015-12-31'] , [1570, '2015-12-31'] , [1502, '2015-12-31'] , [1486, '2015-12-31'] , [1485, '2015-12-31'] , [1483, '2015-12-31'] , [1505, '2015-12-31'] , [1520, '2015-12-31'] , [1521, '2015-12-31'] , [1492, '2015-12-31'] , [1493, '2015-12-31'] , [1503, '2015-12-31'] , [1504, '2015-12-31'] , [1506, '2015-12-31'] , [1536, '2015-12-31'] , [1527, '2015-12-31'] , [1511, '2015-12-31'] , [1519, '2015-12-31'] , [1507, '2015-12-31'] , [1501, '2015-12-31'] , [1580, '2015-12-31'] , [1518, '2015-12-31'] , [1516, '2015-12-31'] , [1528, '2015-12-31'] , [1523, '2015-12-31'] , [1512, '2015-12-31'] , [1513, '2015-12-31'] , [1514, '2015-12-31'] , [1541, '2015-12-31'] , [1542, '2015-12-31'] , [1543, '2015-12-31'] , [1538, '2015-12-31'] , [1540, '2015-12-31'] , [1539, '2015-12-31'] , [1562, '2015-12-31'] , [1565, '2015-12-31'] , [1566, '2015-12-31'] , [1569, '2015-12-31'] , [1574, '2015-12-31'] , [1572, '2015-12-31'] , [1575, '2015-12-31'] , [1577, '2015-12-31'] , [1579, '2015-12-31'] , [1609, '2015-12-31'] , [1606, '2015-12-31'] , [1603, '2015-12-31'] , [1604, '2015-12-31'] , [1608, '2015-12-31'] , [1601, '2015-12-31'] , [1491, '2015-12-31'] , [1564, '2015-12-31'] , [1568, '2015-12-31'] , [1586, '2015-12-31'] , [1582, '2015-12-31'] , [1479, '2015-12-31'] , [1537, '2015-12-31'] , [1531, '2015-12-31'] , [1534, '2015-12-31'] , [1534, '2015-12-31'] , [1349, '2014-12-31'] , [1320, '2014-12-31'] , [1328, '2014-12-31'] , [1471, '2014-12-31'] , [1345, '2014-12-31'] , [1402, '2014-12-31'] , [1335, '2014-12-31'] , [1356, '2014-12-31'] , [1357, '2014-12-31'] , [1280, '2014-12-31'] , [1355, '2014-12-31'] , [1395, '2014-12-31'] , [1431, '2014-12-31'] , [1448, '2014-12-31'] , [1449, '2014-12-31'] , [1482, '2014-12-31'] , [1484, '2014-12-31'] , [1324, '2014-12-31'] , [1322, '2014-12-31'] , [1321, '2014-12-31'] , [1338, '2014-12-31'] , [1339, '2014-12-31'] , [1347, '2014-12-31'] , [1348, '2014-12-31'] , [1329, '2014-12-31'] , [1346, '2014-12-31'] , [1342, '2014-12-31'] , [1326, '2014-12-31'] , [1327, '2014-12-31'] , [1331, '2014-12-31'] , [1325, '2014-12-31'] , [1330, '2014-12-31'] , [1319, '2014-12-31'] , [1340, '2014-12-31'] , [1341, '2014-12-31'] , [1343, '2014-12-31'] , [1368, '2014-12-31'] , [1336, '2014-12-31'] , [1332, '2014-12-31'] , [1333, '2014-12-31'] , [1334, '2014-12-31'] , [1337, '2014-12-31'] , [1446, '2014-12-31'] , [1383, '2014-12-31'] , [1393, '2014-12-31'] , [1394, '2014-12-31'] , [1398, '2014-12-31'] , [1387, '2014-12-31'] , [1386, '2014-12-31'] , [1389, '2014-12-31'] , [1388, '2014-12-31'] , [1403, '2014-12-31'] , [1447, '2014-12-31'] , [1495, '2014-12-31'] , [1496, '2014-12-31'] , [1497, '2014-12-31'] , [1499, '2014-12-31'] , [1500, '2014-12-31'] , [1481, '2014-12-31'] , [1456, '2014-12-31'] , [1457, '2014-12-31'] , [1458, '2014-12-31'] , [1459, '2014-12-31'] , [1460, '2014-12-31'] , [1465, '2014-12-31'] , [1469, '2014-12-31'] , [1470, '2014-12-31'] , [1473, '2014-12-31'] , [1472, '2014-12-31'] , [1475, '2014-12-31'] , [1474, '2014-12-31'] , [1323, '2014-12-31'] , [1367, '2014-12-31'] , [1398, '2014-12-31'] , [1477, '2014-12-31'] , [1494, '2014-12-31']]
        
        last_chase = CountyChaseTime.objects.all().order_by('-id').first()
        for row in c_list:
            obo = CountyChaseProjectOneByOne.objects.get(project__id=row[0])
            if obo.project.purchase_type.value==u'工程' and not obo.act_eng_do_closed:
                obo.act_eng_do_closed = row[1]
            elif obo.project.purchase_type.value==u'勞務' and not obo.act_ser_acceptance_closed:
                obo.act_ser_acceptance_closed = row[1]
            obo.save()
            CountyChaseProjectOneToMany.objects.filter(countychasetime=last_chase, project=obo.project).delete()
