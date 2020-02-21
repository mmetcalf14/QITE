# --------------------------------------------------------------------------
# Source file provided under Apache License, Version 2.0, January 2004,
# http://www.apache.org/licenses/
# (c) Copyright IBM Corp. 2015, 2019
# --------------------------------------------------------------------------

from docplex.mp.progress import SolutionListener, ProgressClock

from docplex.util.environment import get_environment

import os
import six

try:
    import pandas as pd
except ImportError:
    pd = None


class _KpiRecorder(SolutionListener):
    # '''A specialized subclass of :class:`~SolutionListener` that stores the KPI values
    # at each intermediate solution.
    #
    # The `clock` argument defines which events are listened to.
    #
    # See Also:
    #     the enumerated class :class:`~ProgressClock`
    # '''

    def __init__(self, model, clock=ProgressClock.Gap,
                 publish_hook=None,
                 kpi_publish_format=None, absdiff=None, reldiff=None):
        super(_KpiRecorder, self).__init__(clock, absdiff, reldiff)
        self.model = model
        self._context = model.context
        self.publish_hook = publish_hook
        self.kpi_publish_format = kpi_publish_format or 'KPI.%s'
        self.publish_name_fn = lambda kn: self.kpi_publish_format % kn

        # stored dictionaries of kpi values (name: value)
        self._kpi_dicts = []

    def notify_start(self):
        super(_KpiRecorder, self).notify_start()
        self._kpi_dicts = []

    @property
    def nb_reported(self):
        return len(self._kpi_dicts)

    def notify_solution(self, sol):
        pdata = self.current_progress_data

        publish_name_fn = self.publish_name_fn
        # 1. build a dict from formatted names to kpi values.
        name_values = {publish_name_fn(kp.name): kp.compute(sol) for kp in self.model.iter_kpis()}
        # 2. add predefined keys for obj, time.
        name_values['PROGRESS_CURRENT_OBJECTIVE'] = sol.objective_value
        name_values[publish_name_fn('_time')] = pdata.time

        # 3. store it (why???)
        self._kpi_dicts.append(name_values)

        # usually publish kpis in environment...
        if self.publish_hook is not None:
            self.publish_hook(name_values)

        # save kpis.csv table
        context = self._context
        if auto_publising_kpis_table_names(context) is not None:
            write_kpis_table(env=get_environment(),
                             context=context,
                             model=self.model,
                             solution=sol)

    def iter_kpis(self):
        return iter(self._kpi_dicts)

    def __as_df__(self, **kwargs):
        try:
            from pandas import DataFrame
        except ImportError:
            raise RuntimeError("convert as DataFrame: This feature requires pandas")

        df = DataFrame(self._kpi_dicts, **kwargs)
        return df


def encode_csv_string(text):
    """ Encode a string to be used in CSV file

    Args:
        text:  String to encode
    Returns:
        Encoded string, including starting and ending double quote
    """
    res = ['"']
    for c in text:
        res.append(c)
        if c == '"':
            res.append('"')
    res.append('"')
    return ''.join(res)


def write_csv_line(output, line, encoding):
    line = ','.join([encode_csv_string('%s' % c) for c in line])
    output.write(line.encode(encoding))
    output.write('\n'.encode(encoding))


def write_csv(env, table, fields, name):
    # table must be a named tuple
    encoding = 'utf-8'
    with env.get_output_stream(name) as ostr:
        write_csv_line(ostr, fields, encoding)
        for line in table:
            write_csv_line(ostr, line, encoding)

def get_auto_publish_names(context, prop_name, default_name):
    # comparing auto_publish to boolean values because it can be a non-boolean
    autopubs = context.solver.auto_publish
    if autopubs is True:
        return [default_name]
    elif autopubs is False:
        return None
    elif prop_name in autopubs:
        name = autopubs[prop_name]
    else:
        name = None

    if isinstance(name, six.string_types):
        # only one string value: make this the name of the table
        # in a list with one object
        name = [name]
    elif name is True:
        # if true, then use default name:
        name = [default_name]
    elif name is False:
        # Need to compare explicitely to False
        name = None
    else:
        # otherwise the kpi_table_name can be a collection-like of names,
        # just return it
        pass
    return name


def auto_publishing_result_output_names(context):
    # Return the list of result output names for saving
    return get_auto_publish_names(context, 'result_output', 'solution.json')


def auto_publising_kpis_table_names(context):
    # Return the list of kpi table names for saving
    return get_auto_publish_names(context, 'kpis_output', 'kpis.csv')


class PublishResultAsDf(object):
    '''Mixin for classes publishing a result as data frame
    '''

    @staticmethod
    def value_if_defined(obj, attr_name, default=None):
        value = getattr(obj, attr_name) if hasattr(obj, attr_name) else None
        return value if value is not None else default

    def write_output_table(self, df, context,
                           output_property_name=None,
                           output_name=None):
        '''Publishes the output `df`.

        The `context` is used to control the output name:

            - If context.solver.auto_publish is true, the `df` is written using
            output_name.
            - If context.solver.auto_publish is false, This method does nothing.
            - If context.solver.auto_publish.output_property_name is true,
               then `df` is written using output_name.
            - If context.solver.auto_publish.output_propert_name is None or
            False, this method does nothing.
            - If context.solver.auto_publish.output_propert_name is a string,
            it is used as a name to publish the df

        Example:

            A solver can be defined as publishing a result as data frame::

                class SomeSolver(PublishResultAsDf)
                   def __init__(self, output_customizer):
                      # output something if context.solver.autopublish.somesolver_output is set
                      self.output_table_property_name = 'somesolver_output'
                      # output filename unless specified by somesolver_output:
                      self.default_output_table_name = 'somesolver.csv'
                      # customizer if users wants one
                      self.output_table_customizer = output_customizer
                      # uses pandas.DataFrame if possible, otherwise will use namedtuples
                      self.output_table_using_df = True

                    def solve(self):
                        # do something here and return a result as a df
                        result = pandas.DataFrame(columns=['A','B','C'])
                        return result

            Example usage::

               solver = SomeSolver()
               results = solver.solve()
               solver.write_output_table(results)

        '''

        prop = self.value_if_defined(self, 'output_table_property_name')
        prop = output_property_name if output_property_name else prop
        default_name = self.value_if_defined(self, 'default_output_table_name')
        default_name = output_name if output_name else default_name
        names = get_auto_publish_names(context, prop, default_name)
        use_df = self.value_if_defined(self, 'output_table_using_df', True)
        if names:
            env = get_environment()
            customizer = self.value_if_defined(self, 'output_table_customizer', lambda x: x)
            for name in names:
                r = customizer(df)
                if pd and use_df:
                    env.write_df(r, name)
                else:
                    # assume r is a namedtuple
                    write_csv(env, r, r[0]._fields, name)

    def is_publishing_output_table(self, context):
        prop = self.value_if_defined(self, 'output_table_property_name')
        default_name = self.value_if_defined(self, 'default_output_table_name')
        names = get_auto_publish_names(context, prop, default_name)
        return names


def write_kpis(env, kpis_table, name):
    '''Writes a kpis dataframe as file which name is specified.
    The data type depends of extension of name.

    This uses the specfied env to write data as attachments
    '''
    _, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext == '.csv':
        encoding = 'utf-8'
        with env.get_output_stream(name) as ostr:
            write_csv_line(ostr, ['NAME', 'VALUE'], encoding)
            for line in kpis_table:
                write_csv_line(ostr, line, encoding)
    else:
        # right now, only csv is supported
        raise ValueError('file format not supported for KPIs file: %s' % ext)


def write_kpis_table(env, context, model, solution):
    names = auto_publising_kpis_table_names(context)
    kpis_table = []
    for k in model.iter_kpis():
        kpis_table.append([k.name, k.compute(solution)])
    if kpis_table:
        # do not create the kpi tables if there are no kpis to be written
        for name in names:
            write_kpis(env, kpis_table, name)
